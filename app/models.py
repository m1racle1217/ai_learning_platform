from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Module(Base):
    __tablename__ = "modules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    chapters: Mapped[list["Chapter"]] = relationship(back_populates="module")
    days: Mapped[list["LearningDay"]] = relationship(back_populates="module")


class Chapter(Base):
    __tablename__ = "chapters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    module_id: Mapped[int] = mapped_column(ForeignKey("modules.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    goal: Mapped[str] = mapped_column(Text, nullable=False)
    start_day: Mapped[int] = mapped_column(Integer, nullable=False)
    end_day: Mapped[int] = mapped_column(Integer, nullable=False)

    module: Mapped[Module] = relationship(back_populates="chapters")
    days: Mapped[list["LearningDay"]] = relationship(back_populates="chapter")


class LearningDay(Base):
    __tablename__ = "learning_days"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    day_number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    module_id: Mapped[int] = mapped_column(ForeignKey("modules.id"), nullable=False)
    chapter_id: Mapped[int | None] = mapped_column(ForeignKey("chapters.id"))
    stage: Mapped[str] = mapped_column(String(100), nullable=False)
    topic: Mapped[str] = mapped_column(String(200), nullable=False)
    environment: Mapped[str] = mapped_column(Text, nullable=False)
    learning_goal: Mapped[str] = mapped_column(Text, nullable=False)
    resources_text: Mapped[str] = mapped_column(Text, nullable=False)
    resource_hint: Mapped[str] = mapped_column(Text, nullable=False)
    practice_steps: Mapped[str] = mapped_column(Text, nullable=False)
    acceptance_criteria: Mapped[str] = mapped_column(Text, nullable=False)
    output_artifact: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="未开始", nullable=False)
    guidance: Mapped[str] = mapped_column(Text, nullable=False)

    module: Mapped[Module] = relationship(back_populates="days")
    chapter: Mapped[Chapter | None] = relationship(back_populates="days")


class Resource(Base):
    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    day_id: Mapped[int | None] = mapped_column(ForeignKey("learning_days.id"))
    module_id: Mapped[int | None] = mapped_column(ForeignKey("modules.id"))
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    day: Mapped[LearningDay | None] = relationship()


class ResourceProgress(Base):
    __tablename__ = "resource_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    resource_id: Mapped[int] = mapped_column(ForeignKey("resources.id"), unique=True, nullable=False)
    completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ExerciseSubmission(Base):
    __tablename__ = "exercise_submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    day_id: Mapped[int] = mapped_column(ForeignKey("learning_days.id"), nullable=False)
    answer_text: Mapped[str] = mapped_column(Text, nullable=False)
    output_path: Mapped[str | None] = mapped_column(Text)
    checklist_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    auto_status: Mapped[str] = mapped_column(String(20), nullable=False)
    auto_feedback: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    day_id: Mapped[int | None] = mapped_column(ForeignKey("learning_days.id"))
    module_id: Mapped[int | None] = mapped_column(ForeignKey("modules.id"))
    question_type: Mapped[str] = mapped_column(String(20), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    options_json: Mapped[str] = mapped_column(Text, nullable=False)
    correct_answer_json: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    day_id: Mapped[int | None] = mapped_column(ForeignKey("learning_days.id"))
    module_id: Mapped[int | None] = mapped_column(ForeignKey("modules.id"))
    score: Mapped[float] = mapped_column(Float, nullable=False)
    total: Mapped[int] = mapped_column(Integer, nullable=False)
    feedback_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class UserEvent(Base):
    __tablename__ = "user_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    target_type: Mapped[str | None] = mapped_column(String(80))
    target_id: Mapped[int | None] = mapped_column(Integer)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
