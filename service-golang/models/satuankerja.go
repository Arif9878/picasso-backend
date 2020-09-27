package models

import (
	"github.com/jinzhu/gorm"
	uuid "github.com/satori/go.uuid"
)

//satuan kerja models
type SatuanKerja struct {
	BaseModel
	Parent          *SatuanKerja `gorm:"foreignkey:ID"`
	ParentID        string       `gorm:"size:40;index" json:"parent_id"`
	NameParent      string       `gorm:"size:64" json:"name_parent"`
	NameSatuanKerja string       `gorm:"size:64" json:"name_satuan_kerja, omitempty"`
	Description     string       `gorm:"size:255" json:"description"`
	CreatedBy       string       `json:"created_by"`
	UpdatedBy       string       `json:"updated_by"`
}

// BeforeCreate will set a UUID rather than numeric ID.
func (base *SatuanKerja) BeforeCreate(scope *gorm.Scope) error {
	uuid := uuid.NewV4()
	return scope.SetColumn("ID", uuid)
}
