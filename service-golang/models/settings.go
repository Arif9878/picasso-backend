package models

//Settings models
type Settings struct {
	BaseModel
	SettingName  string `gorm:"size:60;index" json:"setting_name"`
	SettingKey   string `gorm:"size:30" json:"setting_key"`
	SettingValue string `gorm:"size:60;index" json:"setting_value, omitempty"`
	CreatedByID  string `json:"created_by_id"`
	CreatedBy    string `json:"created_by"`
	UpdatedByID  string `json:"updated_by_id"`
	UpdatedBy    string `json:"updated_by"`
}
