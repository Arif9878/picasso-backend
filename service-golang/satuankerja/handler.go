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

func (config *ConfigDB) listSatuanKerja(w http.ResponseWriter, r *http.Request) {
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

	var satker []models.SatuanKerja

	if err := config.db.Model(&models.SatuanKerja{}).
		Where("name_satuan_kerja ILIKE ?", "%"+search+"%").
		Order("created_at DESC").
		Count(&total).
		Offset(page).
		Limit(limit).
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

func (config *ConfigDB) postSatuanKerja(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context().Value("user")
	sessionUser := ctx.(*jwt.Token).Claims.(jwt.MapClaims)
	decoder := json.NewDecoder(r.Body)
	payload := models.SatuanKerja{}
	if err := decoder.Decode(&payload); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	strSession := sessionUser["email"]
	userSession := strSession.(string)
	var parent models.SatuanKerja
	if payload.ParentID != "" {
		if err := config.db.Where("ID = ?", payload.ParentID).Find(&parent).Error; err != nil {
			utils.ResponseError(w, http.StatusNotFound, "Parent ID Not Found")
			return
		}
	}

	create := models.SatuanKerja{
		ParentID:        payload.ParentID,
		NameParent:      parent.NameSatuanKerja,
		NameSatuanKerja: payload.NameSatuanKerja,
		Description:     payload.Description,
		CreatedBy:       userSession,
	}

	if err := config.db.Create(&create).Error; err != nil {
		utils.ResponseError(w, http.StatusBadRequest, "Invalid body")
		return
	}
	response := config.db.Model(&create).Related(&parent, "ID")
	utils.ResponseOk(w, response.Value)
}

func (config *ConfigDB) putSatuanKerja(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	params := mux.Vars(r)
	ctx := r.Context().Value("user")
	sessionUser := ctx.(*jwt.Token).Claims.(jwt.MapClaims)
	decoder := json.NewDecoder(r.Body)
	payload := models.SatuanKerja{}
	if err := decoder.Decode(&payload); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	strSession := sessionUser["email"]
	userSession := strSession.(string)

	var parent models.SatuanKerja
	if payload.ParentID != "" {
		if err := config.db.Where("ID = ?", payload.ParentID).Find(&parent).Error; err != nil {
			utils.ResponseError(w, http.StatusNotFound, "Parent ID Not Found")
			return
		}
	}
	update := models.SatuanKerja{
		ParentID:        payload.ParentID,
		NameParent:      parent.NameSatuanKerja,
		NameSatuanKerja: payload.NameSatuanKerja,
		Description:     payload.Description,
		CreatedBy:       userSession,
	}

	if err := config.db.Model(&payload).Where("ID = ?", params["id"]).Update(&update).Error; err != nil {
		utils.ResponseError(w, http.StatusBadRequest, "Invalid body")
		return
	}
	response := config.db.Model(&update).Related(&parent, "Parent")
	utils.ResponseOk(w, response.Value)
}

func (config *ConfigDB) detailSatuanKerja(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	params := mux.Vars(r)
	var response models.SatuanKerja
	if err := config.db.Where("ID = ?", params["id"]).Find(&response).Error; err != nil {
		utils.ResponseError(w, http.StatusBadRequest, "Data Not Found")
		return
	}
	result := models.ResultsData{
		Status:  http.StatusOK,
		Success: true,
		Results: response,
	}
	utils.ResponseOk(w, result)
}

func (config *ConfigDB) deleteSatuanKerja(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	params := mux.Vars(r)
	payload := models.SatuanKerja{}
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
