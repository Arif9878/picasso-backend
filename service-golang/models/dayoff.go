package models

import (
	"time"

	"go.mongodb.org/mongo-driver/bson/primitive"
)

//DayOff models
type DayOff struct {
	ID                 primitive.ObjectID     `json:"_id,omitempty" bson:"_id,omitempty"`
	StartDate          time.Time              `json:"start_date,omitempty" bson:"start_date,omitempty" binding:"required"`
	EndDate            time.Time              `json:"end_date,omitempty" bson:"end_date,omitempty" binding:"required"`
	PermitsType        string                 `json:"permits_type,omitempty" bson:"permits_type,omitempty" binding:"required"`
	PermitAcknowledged []string               `json:"permit_acknowledged,omitempty" bson:"permit_acknowledged,omitempty" binding:"required"`
	Note               string                 `json:"note,omitempty" bson:"note,omitempty" binding:"required"`
	FilePath           string                 `json:"file_path,omitempty" bson:"file_path,omitempty" binding:"required" default:nil`
	FileURL            string                 `json:"file_url,omitempty" bson:"file_url,omitempty" binding:"required" default:nil`
	CreatedAt          time.Time              `json:"created_at,omitempty" bson:"created_at,omitempty" binding:"required"`
	CreatedBy          map[string]interface{} `json:"created_by,omitempty" bson:"created_by,omitempty" binding:"required"`
	UpdatedAt          time.Time              `json:"updated_at,omitempty" bson:"updated_at,omitempty" binding:"required"`
	UpdatedBy          map[string]interface{} `json:"updated_by,omitempty" bson:"updated_by,omitempty" binding:"required"`
}
