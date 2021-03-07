# 4. First Use Case

## 4b. User Repository

Let's look at the _UserRepository_ which will be the persistence layer for our user entities.

A repository should implement very simple methods to interact with the storage medium. Any logic should be implemented in the service and use case layers. Basic methods are also more likely to be supported by different storage technologies which supports our desire to be independent from a specific implementation, platform or service.

The repository needs to support the following operations:

1. Get a single entity via its identify (`id`)
2. Store a new entity
3. Update an existing entity
4. Remove an entity from storage
5. Find several entities via given attribute values
6. Find all users (for admin use)
7. Get several entities via a list of identifiers

The first 4 are the standard CRUD operations and the fifth allows us to _search_ for entities.

The last two are optimisation to avoid multiple independent network requests for a single record when the technology used allows us to combine these in a single call. This can be seen as an optimisation for a specific implementation (databases, in this case) but without these methods we have no option to optimise for this type of access. For technologies that do not support a combined request it is easy enough to simulate with individual requests.

> You can define more specialised methods to take advantage of the strength of your data store. For example you could define a dedicated `user_with_friends` method to load user and their friends via a single call to a RDBMS. But keep in mind that you have to write a replacement for this method if you have to base a repository implementation on a storage technology that does not support relations.

### The _UserRepositoryInterface_

In a typed language we can define an _interface_ to specify the details of these methods and the language will enforce that the methods are implemented correctly.

In Python we can use the optional type annotation syntax to check that the input and return types are correct. At the class level we can use the [abc](https://docs.python.org/3/library/abc.html) package to define `abstract` methods for our interface. These methods raise an error if they are called so any subclass has to implement them to avoid errors at run time. I have also added a `__subclasshook__` to enforce that all methods are implemented by the subclass.

Here is the setup of our `UserRepositoryInterface` (and any other interface we will write):

```python
# src/app/domain/users/interfaces.py
import abc
from typing import List, Optional

from app.domain.utils import implements_interface

from .entities import User


class UserRepositoryInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return implements_interface(cls, subclass) or NotImplemented
```

#### Listing users

We have two methods that return a list of users. Two fullfil this contract our implementation has to return a list (and nothing but a list) and all elements in this list have to be instances of the User entity. `None` values in the list are not allowed.

If you have an editor that supports type hints it will highlight if your code could produce results that to not match the requirements of the interface. Look out for those highlights.

> In a real programme we would add pagination arguments to every method that returns a list. In this demo app we can get by without.

```python
    @abc.abstractmethod
    async def find_all(self) -> List[User]:
        """return a list of all users"""
        raise NotImplementedError

    @abc.abstractmethod
    async def find_users_by_attributes(self, attributes: dict) -> List[User]:
        """return list of users with given attribute values"""
        raise NotImplementedError
```

#### Searching for users

The `find_users_by_attributes` method is based no an _equality check_ of user attributes. We should also add a method to list users based on a set of search strings. For example we would like to list users with first names starting with "Z" or users that are on the platform for longer than 3 years. Expressing these search options in code is quite complicated and we won't use this feature for our demo app. It is left as an exercise for the reader.

#### Looking up individual users

We will look up individual users by their `id`. We have to take into account that there is no user for a given `id` or that the returned data can not be converted to a user entity. In this case we return `None` and the calling function has to handle this case accordingly. This is expressed in the method signature: `Optional[User]`.

The `get_users_by_ids` method again returns a list of users. When we implement it we have to take care to eliminate all `None` or incomplete data results before we return the list.

```python
    @abc.abstractmethod
    async def get_user_by_id(self, id: str) -> Optional[User]:
        """find and return one user via the user's id"""
        raise NotImplementedError

    @abc.abstractmethod
    async def get_users_by_ids(self, ids: List[str]) -> List[User]:
        """find list of users via their ids"""
        raise NotImplementedError
```

#### Save a new user

A new user is created from the input data in the form of a `NewUserDTO` object. The `NewUserDTO` has the same fields as the `User` entity except for the `id`. It is the job of the `save_new_user` method to assign an id and to store the data. The repository is the best place to generate a new id (the 'primary key'). If there are any restrictions for the id field, the repository will implement them correctly.

I added the `DTO` to the name to show that this entity has a single use case: To hold the data of a new user before that user is created.

We do not impose any other requirements on the data. For example, from the point of view of the repository it is acceptable to have two users with the same email address. They will still be different records based on their distinct ids. The rest of our programme may require emails to be unique. In that case we have to implement additional checks in our business logic layer before we create a new user.

The method has no way to indicate to the calling function if there was an error during the operation. If we encounter an exception, we expect the higher levels to handle it within their context. This principle is known as _Return successful or not at all._ It keeps our interface small and delegates error handling to the business logic layer.

> The NewUserDTO also has an additional `password_hash` field that we will need when we implement authentication.

```python
    @abc.abstractmethod
    async def save_new_user(self, data: NewUserDTO) -> User:
        """create new record and return user"""
        raise NotImplementedError
```

#### Update an existing user

To update a user we pass in the (updated) user and return a user as the result. Note that two instances do not have to be the same. When our method does some updates on its own (for example to set a time stamp) we would have to return a new user object that is based on the updated data.

We also have no option to return an error to the calling function. We just let the error propagate to the higher level code where it can be handled.

```python
    @abc.abstractmethod
    async def update_user(self, user: User) -> User:
        """update an existing user in storage"""
        raise NotImplementedError
```

#### Delete a user

Finally, we add a delete method to remove users from the system. This is a
_hard_ delete action that removes the data from the system altogether. The repository is not responsible to maintain completeness of your data. You need to check in your use cases if the user can safely be deleted before you call this method.

```python
    @abc.abstractmethod
    async def delete_user(self, id: str) -> bool:
        """delete a user from storage"""
        raise NotImplementedError
```
