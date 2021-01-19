package models

import (
	"github.com/jinzhu/gorm"
	uuid "github.com/satori/go.uuid"
)

//tupoksi jabatan models
type TupoksiJabatan struct {
	BaseModel
	Jabatan       Jabatan   `gorm:"foreignkey:JabatanID,constraint:OnUpdate:CASCADE,OnDelete:SET NULL;,unique" json:"jabatan"`
	JabatanID     uuid.UUID `json:"jabatan_id"`
	NameTupoksi   string    `gorm:"size:200" json:"name_tupoksi"`
	TargetTupoksi int       `gorm:"type:integer" json:"target_tupoksi, omitempty"`
	Sequence      int       `gorm:"type:integer" json:"sequence"`
	Description   string    `gorm:"type:text" json:"description"`
	CreatedBy     string    `json:"created_by"`
	UpdatedBy     string    `json:"updated_by"`
}

// BeforeCreate will set a UUID rather than numeric ID.
func (base *TupoksiJabatan) BeforeCreate(scope *gorm.Scope) error {
	uuid := uuid.NewV4()
	return scope.SetColumn("ID", uuid)
}

type ResultListTupoksiJabatan struct {
	BaseModel
	JabatanID     string `json:"jabatan_id"`
	NameTupoksi   string `json:"name_tupoksi"`
	TargetTupoksi int    `json:"target_tupoksi, omitempty"`
	Sequence      int    `json:"sequence"`
	Description   string `json:"description"`
	CreatedBy     string `json:"created_by"`
	UpdatedBy     string `json:"updated_by"`
}
