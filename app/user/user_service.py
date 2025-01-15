from app.user.user_repository import UserRepository
from app.user.user_schema import User, UserLogin, UserUpdate

class UserService:
    def __init__(self, userRepoitory: UserRepository) -> None:
        self.repo = userRepoitory

    def login(self, user_login: UserLogin) -> User:
        """
        Logs in a user.

        Args:
            user_login (UserLogin): The user login details.

        Returns:
            User: The logged-in user's details.
        """
        user = self.repo.get_user_by_email(user_login.email)
        if not user:
            raise ValueError("User not Found.")
        if user.password != user_login.password:
            raise ValueError("Invalid ID/PW")
        return user
        
    def register_user(self, new_user: User) -> User:
        """
        Registers a new user.

        Args:
            new_user (User): The new user details.

        Returns:
            User: The registered user's details.
        """
        existing_user = self.repo.get_user_by_email(new_user.email)
        if existing_user:
            raise ValueError("User already Exists.")
        return self.repo.save_user(new_user)

    def delete_user(self, email: str) -> User:
        """
        Deletes a user.

        Args:
            email (str): The email of the user to delete.

        Returns:
            User: The deleted user's details.
        """
        user = self.repo.get_user_by_email(email)
        if not user:
            raise ValueError("User not Found.")
        return self.repo.delete_user(user)

    def update_user_pwd(self, user_update: UserUpdate) -> User:
        """
        Updates a user's password.

        Args:
            user_update (UserUpdate): The user's email and new password.

        Returns:
            User: The updated user's details.
        """
        user = self.repo.get_user_by_email(user_update.email)
        if not user:
            raise ValueError("User not Found.")
        user.password = user_update.new_password
        return self.repo.save_user(user)
        