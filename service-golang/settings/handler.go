package main

import (
	"encoding/json"
	"net/http"
	"strconv"

	"github.com/dgrijalva/jwt-go"
	"github.com/gorilla/mux"

	"github.com/jabardigitalservice/picasso-backend/service-golang/models"
	"github.com/jabardigitalservice/picasso-backend/service-golang/utils"
)

func (config *ConfigDB) listSettings(w http.ResponseWriter, r *http.Request) {
	search := string(r.URL.Query().Get("search"))
	page, err := strconv.Atoi(r.URL.Query().Get("page"))
	if err != nil {
		page = 0
	} else {
		page--
	}
	limit, err := strconv.Atoi(r.URL.Query().Get("limit"))
	if err != nil {
		limit = 20
	}
	var total int

	var satker []models.Settings

	if err := config.db.Model(&models.Settings{}).
		Where("setting_name ILIKE ?", "%"+search+"%").
		Order("created_at DESC").
		Count(&total).
		Limit(limit).
		Offset(page).
		Find(&satker).Error; err != nil {
		utils.ResponseError(w, http.StatusBadRequest, "Invalid body")
		return
	}

	metaData := models.MetaData{
		TotalCount:  total,
		TotalPage:   utils.PageCount(total, limit),
		CurrentPage: utils.CurrentPage(page, limit),
		PerPage:     limit,
	}

	result := models.ResultsData{
		Status:  http.StatusOK,
		Success: true,
		Results: satker,
		Meta:    metaData,
	}

	utils.ResponseOk(w, result)
}

func (config *ConfigDB) postSettings(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context().Value("user")
	sessionUser := ctx.(*jwt.Token).Claims.(jwt.MapClaims)
	decoder := json.NewDecoder(r.Body)
	payload := models.Settings{}
	if err := decoder.Decode(&payload); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	create := models.Settings{
		SettingName:  payload.SettingName,
		SettingKey:   payload.SettingKey,
		SettingValue: payload.SettingValue,
		CreatedByID:  sessionUser["user_id"].(string),
		CreatedBy:    sessionUser["email"].(string),
	}

	if err := config.db.Create(&create).Error; err != nil {
		utils.ResponseError(w, http.StatusBadRequest, "Invalid body")
		return
	}

	utils.ResponseOk(w, create)
}

func (config *ConfigDB) putSettings(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	params := mux.Vars(r)
	ctx := r.Context().Value("user")
	sessionUser := ctx.(*jwt.Token).Claims.(jwt.MapClaims)
	decoder := json.NewDecoder(r.Body)
	payload := models.Settings{}
	if err := decoder.Decode(&payload); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	update := models.Settings{
		SettingName:  payload.SettingName,
		SettingKey:   payload.SettingKey,
		SettingValue: payload.SettingValue,
		UpdatedByID:  sessionUser["user_id"].(string),
		UpdatedBy:    sessionUser["email"].(string),
	}

	if err := config.db.Model(&payload).Where("ID = ?", params["id"]).Update(&update).Error; err != nil {
		utils.ResponseError(w, http.StatusBadRequest, "Invalid body")
		return
	}

	utils.ResponseOk(w, update)
}

func (config *ConfigDB) deleteSettings(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	params := mux.Vars(r)
	payload := models.Settings{}
	if err := config.db.First(&payload, "ID = ?", params["id"]).Error; err != nil {
		utils.ResponseError(w, http.StatusBadRequest, "Data Not Found")
		return
	}
	if err := config.db.Model(&payload).Where("ID = ?", params["id"]).Delete(&payload).Error; err != nil {
		utils.ResponseError(w, http.StatusBadRequest, "Data Not Found")
		return
	}
	result := models.ResultsData{
		Status:  http.StatusOK,
		Success: true,
		Message: `Data Berhasil Di Hapus`,
	}

	utils.ResponseOk(w, result)
}
