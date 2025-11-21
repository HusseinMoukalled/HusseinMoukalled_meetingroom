from shared.database import Base,engine
from users_service.app import models as user_models
from rooms_service.app import models as room_models
from bookings_service.app import models as booking_models
from reviews_service.app import models as review_models

Base.metadata.create_all(bind=engine)
