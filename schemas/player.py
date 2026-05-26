from pydantic import BaseModel, field_validator


class PlayerCreate(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def name_nao_vazio(cls, v):
        if not v.strip():
            raise ValueError("Nome não pode ser vazio.")
        return v.strip()


class PlayerLogin(BaseModel):
    player_id: int
