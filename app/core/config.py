from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    mongodb_uri: str = "mongodb+srv://mohamedghoul:MPGfAcf8WEy8qL78@cluster0.uufrj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    database_name: str = "chatbot"
    collection_name: str = "conversations"
    class Config:
        env_file = ".env"
settings = Settings()
