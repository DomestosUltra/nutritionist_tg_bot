from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.app.db.models import UserInteraction


async def create_user_interaction(
    db: AsyncSession,
    user_id: str,
    username: str,
    user_query: str,
    bot_response: str = None,
) -> UserInteraction:
    """
    Save user interaction to database
    """
    db_interaction = UserInteraction(
        user_id=user_id,
        username=username,
        user_query=user_query,
        bot_response=bot_response,
    )

    db.add(db_interaction)
    await db.commit()
    await db.refresh(db_interaction)

    return db_interaction


async def get_user_interactions(
    db: AsyncSession, user_id: str, limit: int = 10
) -> list[UserInteraction]:
    """
    Get user interaction history
    """
    query = (
        select(UserInteraction)
        .where(UserInteraction.user_id == user_id)
        .order_by(UserInteraction.created_at.desc())
        .limit(limit)
    )

    result = await db.execute(query)
    return result.scalars().all()


async def update_interaction_response(
    db: AsyncSession, interaction_id: int, bot_response: str
) -> UserInteraction:
    """
    Update the response for a previously stored interaction
    """
    query = select(UserInteraction).where(UserInteraction.id == interaction_id)
    result = await db.execute(query)
    interaction = result.scalar_one_or_none()

    if interaction:
        interaction.bot_response = bot_response
        await db.commit()
        await db.refresh(interaction)

    return interaction
