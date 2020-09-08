package models

import (
	"time"

	"go.mongodb.org/mongo-driver/bson/primitive"
)

type MessageNotification struct {
	ID             primitive.ObjectID     `json:"_id,omitempty" bson:"_id,omitempty"`
	PurposeMessage string                 `json:"purpose_message,omitempty" bson:"purpose_message,omitempty" binding:"required"`
	Message        string                 `json:"message,omitempty" bson:"message,omitempty" binding:"required"`
	CreatedBy      map[string]interface{} `json:"created_by,omitempty" bson:"created_by,omitempty" binding:"required"`
	CreatedAt      time.Time              `json:"created_at,omitempty" bson:"created_at,omitempty" binding:"required"`
}
