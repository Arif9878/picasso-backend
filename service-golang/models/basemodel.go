package models

import (
	"time"

	"github.com/jinzhu/gorm"
	uuid "github.com/satori/go.uuid"
)

type BaseModel struct {
	ID        uuid.UUID `gorm:"type:uuid;primary_key;" json:"id"`
	CreatedAt time.Time
	UpdatedAt time.Time
	DeletedAt *time.Time
}

// BeforeCreate will set a UUID rather than numeric ID.
func (base *BaseModel) BeforeCreate(scope *gorm.Scope) error {
	uuid := uuid.NewV4()
	return scope.SetColumn("ID", uuid)
}

func (m *BaseModel) BeforeInsert(db *gorm.Scope) error {
	now := time.Now()
	if m.CreatedAt.IsZero() {
		m.CreatedAt = now
	}
	return nil
}

func (m *BaseModel) BeforeUpdate(db *gorm.Scope) error {
	m.UpdatedAt = time.Now()
	return nil
}
