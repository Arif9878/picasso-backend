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

func (config *ConfigDB) listJabatan(w http.ResponseWriter, r *http.Request) {
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

	var jabatan []models.Jabatan

	if err := config.db.Model(&models.Jabatan{}).
		Where("name_jabatan ILIKE ?", "%"+search+"%").
		Order("created_at DESC").
		Count(&total).
		Offset(page).
		Limit(limit).
		Find(&jabatan).Error; err != nil {
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
		Results: jabatan,
		Meta:    metaData,
	}

	utils.ResponseOk(w, result)
}

func (config *ConfigDB) listJabatanBySatuanKerja(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	params := mux.Vars(r)
	var jabatan []models.Jabatan
	page, err := strconv.Atoi(r.URL.Query().Get("page"))
	if err != nil {
		page = 0
	} else {
		page--
	}
	limit, err := strconv.Atoi(r.URL.Query().Get("limit"))
	if err != nil {
		limit = 100
	}
	var total int
	if err := config.db.Model(&models.Jabatan{}).
		Where("satuan_kerja_id = ?", params["id"]).
		Order("created_at DESC").
		Count(&total).
		Offset(page).
		Limit(limit).
		Find(&jabatan).Error; err != nil {
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
		Results: jabatan,
		Meta:    metaData,
	}
	utils.ResponseOk(w, result)
}

func (config *ConfigDB) postJabatan(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context().Value("user")
	sessionUser := ctx.(*jwt.Token).Claims.(jwt.MapClaims)
	decoder := json.NewDecoder(r.Body)
	payload := models.Jabatan{}
	if err := decoder.Decode(&payload); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	strSession := sessionUser["email"]
	userSession := strSession.(string)
	var satuankerja models.SatuanKerja
	if err := config.db.Where("ID = ?", payload.SatuanKerjaID).Find(&satuankerja).Error; err != nil {
		utils.ResponseError(w, http.StatusNotFound, "SatuanKerjaID ID Not Found")
		return
	}

	create := models.Jabatan{
		SatuanKerjaID:   payload.SatuanKerjaID,
		NameSatuanKerja: satuankerja.NameSatuanKerja,
		NameJabatan:     payload.NameJabatan,
		Description:     payload.Description,
		CreatedBy:       userSession,
	}

	if err := config.db.Create(&create).Error; err != nil {
		utils.ResponseError(w, http.StatusBadRequest, "Invalid body")
		return
	}

	utils.ResponseOk(w, create)
}

func (config *ConfigDB) putJabatan(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	params := mux.Vars(r)
	ctx := r.Context().Value("user")
	sessionUser := ctx.(*jwt.Token).Claims.(jwt.MapClaims)
	decoder := json.NewDecoder(r.Body)
	payload := models.Jabatan{}
	if err := decoder.Decode(&payload); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	strSession := sessionUser["email"]
	userSession := strSession.(string)
	// check id jabatan
	if err := config.db.Where("ID = ?", params["id"]).Find(&models.Jabatan{}).Error; err != nil {
		utils.ResponseError(w, http.StatusNotFound, "ID Not Found")
		return
	}

	var satuankerja models.SatuanKerja
	if payload.SatuanKerjaID != "" {
		if err := config.db.Where("ID = ?", payload.SatuanKerjaID).Find(&satuankerja).Error; err != nil {
			utils.ResponseError(w, http.StatusNotFound, "Parent ID Not Found")
			return
		}
	}
	update := models.Jabatan{
		SatuanKerjaID:   payload.SatuanKerjaID,
		NameSatuanKerja: satuankerja.NameSatuanKerja,
		NameJabatan:     payload.NameJabatan,
		Description:     payload.Description,
		CreatedBy:       userSession,
	}

	if err := config.db.Model(&payload).Where("ID = ?", params["id"]).Update(&update).Error; err != nil {
		utils.ResponseError(w, http.StatusBadRequest, "Invalid body")
		return
	}

	utils.ResponseOk(w, update)
}

func (config *ConfigDB) detailJabatan(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	params := mux.Vars(r)
	var response models.Jabatan
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

func (config *ConfigDB) deleteJabatan(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	params := mux.Vars(r)
	payload := models.Jabatan{}
	// check id jabatan
	if err := config.db.Where("ID = ?", params["id"]).Find(&payload).Error; err != nil {
		utils.ResponseError(w, http.StatusNotFound, "ID Not Found")
		return
	}
	if err := config.db.Model(&payload).Where("ID = ?", params["id"]).Delete(&payload).Error; err != nil {
		utils.ResponseError(w, http.StatusBadRequest, "Data Not Found")
		return
	}
	response := "Data Berhasil Di Hapus"
	utils.ResponseOk(w, response)
}
