package models

import "go.mongodb.org/mongo-driver/bson/primitive"

type DeviceToken struct {
	ID          primitive.ObjectID `json:"_id,omitempty" bson:"_id,omitempty"`
	UserID      string             `json:"userID,omitempty" bson:"userID,omitempty" binding:"required"`
	AppID       string             `json:"appID,omitempty" bson:"appID,omitempty" binding:"required"`
	DeviceToken string             `json:"deviceToken,omitempty" bson:"deviceToken,omitempty" binding:"required"`
}
