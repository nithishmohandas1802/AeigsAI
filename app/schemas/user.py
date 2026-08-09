from pydantic import BaseModel, EmailStr, Field, model_validator

class UserCreate(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=100,
    )
    email: EmailStr

class UserUpdate(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=100,
    )
    email: EmailStr

class UserPatch(BaseModel):
    username: str | None = Field(
        default=None,
        min_length=3,
        max_length=100,
    )
    email: EmailStr | None = None

    @model_validator(mode="after")
    def validate_at_least_one_field(self):
        if self.username is None and self.email is None:
            raise ValueError(
                "At least one field must be provided for update"
            )

        return self
    
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    model_config = {
        "from_attributes": True
    }