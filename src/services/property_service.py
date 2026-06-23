from database.models import Property, PropertyImage
from database.db import db
from sqlalchemy.orm import joinedload

def get_properties_with_thumbnails():
    """
    Fetches all properties joined with their primary thumbnail image.
    """
    # We join Property with PropertyImage where is_thumbnail is True
    properties = Property.query.outerjoin(
        PropertyImage, 
        (Property.id == PropertyImage.property_id) & (PropertyImage.is_thumbnail == True)
    ).add_columns(
        Property.id, 
        Property.title, 
        Property.location, 
        Property.province,
        PropertyImage.image_url
    ).all()
    
    return properties

def set_property_thumbnail(property_id, image_id):
    """
    Ensures only one image is marked as thumbnail for a property.
    """
    # 1. Reset all images for this property to False
    db.session.query(PropertyImage).filter_by(property_id=property_id).update({"is_thumbnail": False})
    
    # 2. Set the specific image as the thumbnail
    db.session.query(PropertyImage).filter_by(id=image_id).update({"is_thumbnail": True})
    db.session.commit()