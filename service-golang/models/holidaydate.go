package models

import (
	"time"

	"go.mongodb.org/mongo-driver/bson/primitive"
)

//HolidayDate models
type HolidayDate struct {
	ID          primitive.ObjectID     `json:"_id,omitempty" bson:"_id,omitempty"`
	HolidayDate time.Time              `json:"holiday_date,omitempty" bson:"holiday_date,omitempty" binding:"required"`
	HolidayType string                 `json:"holiday_type,omitempty" bson:"holiday_type,omitempty" binding:"required"`
	HolidayName string                 `json:"holiday_name,omitempty" bson:"holiday_name,omitempty" binding:"required"`
	CreatedAt   time.Time              `json:"created_at,omitempty" bson:"created_at,omitempty" binding:"required"`
	CreatedBy   map[string]interface{} `json:"created_by,omitempty" bson:"created_by,omitempty" binding:"required"`
	UpdatedAt   time.Time              `json:"updated_at,omitempty" bson:"updated_at,omitempty" binding:"required"`
	UpdatedBy   map[string]interface{} `json:"updated_by,omitempty" bson:"updated_by,omitempty" binding:"required"`
}

type HolidayDateResponse struct {
	ID          primitive.ObjectID `json:"_id,omitempty" bson:"_id,omitempty"`
	HolidayDate time.Time          `json:"holiday_date,omitempty" bson:"holiday_date,omitempty" binding:"required"`
	HolidayType string             `json:"holiday_type,omitempty" bson:"holiday_type,omitempty" binding:"required"`
	HolidayName string             `json:"holiday_name,omitempty" bson:"holiday_name,omitempty" binding:"required"`
}
