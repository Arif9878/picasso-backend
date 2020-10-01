package models

import (
	"time"

	"go.mongodb.org/mongo-driver/bson/primitive"
)

//Attendance models
type Attendance struct {
	ID          primitive.ObjectID      `json:"_id,omitempty" bson:"_id,omitempty"`
	StartDate   time.Time               `json:"startDate,omitempty" bson:"startDate,omitempty" binding:"required"`
	EndDate     time.Time               `json:"endDate,omitempty" bson:"endDate,omitempty" binding:"required"`
	OfficeHours int32                   `json:"officeHours,omitempty" bson:"officeHours,omitempty" binding:"required"`
	Location    string                  `json:"location,omitempty" bson:"location,omitempty" binding:"required"`
	Message     string                  `json:"message,omitempty" bson:"message,omitempty" binding:"required"`
	CreatedAt   time.Time               `json:"createdAt,omitempty" bson:"createdAt,omitempty" binding:"required"`
	UpdatedAt   *time.Time              `json:"updatedAt,omitempty" bson:"updatedAt,omitempty" binding:"required"`
	CreatedBy   map[string]interface{}  `json:"createdBy,omitempty" bson:"createdBy,omitempty" binding:"required"`
	UpdatedBy   *map[string]interface{} `json:"updatedBy,omitempty" bson:"updatedBy,omitempty" binding:"required"`
}
