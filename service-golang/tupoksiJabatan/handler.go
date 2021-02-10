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

func (config *ConfigDB) listTupoksiJabatan(w http.ResponseWriter, r *http.Request) {
	search := string(r.URL.Query().Get("search"))
	JabatanID := string(r.URL.Query().Get("jabatan_id"))
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

	var results []models.TupoksiJabatanResultList

	sqlStatement := "deleted_at IS NULL AND name_tupoksi ILIKE " + "'%" + search + "%'"
	if JabatanID != "" {
		sqlStatement += " AND jabatan_id = " + "'" + JabatanID + "'"
	}
	if err := config.db.Table("tupoksi_jabatans").
		Where(sqlStatement).
		Order("sequence ASC, created_at DESC").
		Count(&total).
		Offset(page).
		Limit(limit).
		Find(&results).Error; err != nil {
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
		Results: results,
		Meta:    metaData,
	}

	utils.ResponseOk(w, result)
}

func (config *ConfigDB) listTupoksiJabatanByUser(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context().Value("user")
	sessionUser := ctx.(*jwt.Token).Claims.(jwt.MapClaims)
	idJabatan := sessionUser["id_jabatan"].(string)

	var listTupoksi []models.TupoksiJabatanResultList
	var tupoksiDiluarTugas models.TupoksiJabatanResultList
	if err := config.db.Table("tupoksi_jabatans").Where("ID = ?", utils.GetEnv("TUPOKSI_DILUAR_TUGAS")).First(&tupoksiDiluarTugas).Error; err != nil {
		utils.ResponseError(w, http.StatusBadRequest, "Data Not Found")
		return
	}
	if err := config.db.Table("tupoksi_jabatans").
		Where("jabatan_id = $1 AND deleted_at IS NULL", idJabatan).
		Order("sequence ASC").
		Find(&listTupoksi).Error; err != nil {
		utils.ResponseError(w, http.StatusNotFound, "Tupoksi Jabatan belum ada pada Jabatan User")
		return
	}
	result := append(listTupoksi, tupoksiDiluarTugas)
	results := models.ResultsData{
		Status:  http.StatusOK,
		Success: true,
		Results: result,
	}

	utils.ResponseOk(w, results)
}

func (config *ConfigDB) postTupoksiJabatan(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context().Value("user")
	sessionUser := ctx.(*jwt.Token).Claims.(jwt.MapClaims)
	decoder := json.NewDecoder(r.Body)
	payload := models.TupoksiJabatan{}
	if err := decoder.Decode(&payload); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	strSession := sessionUser["email"]
	userSession := strSession.(string)
	var jabatan models.Jabatan
	if err := config.db.Where("ID = ?", payload.JabatanID).Find(&jabatan).Error; err != nil {
		utils.ResponseError(w, http.StatusNotFound, "JabatanID ID Not Found")
		return
	}

	create := models.TupoksiJabatan{
		Jabatan:       jabatan,
		JabatanID:     jabatan.ID,
		NameTupoksi:   payload.NameTupoksi,
		TargetTupoksi: payload.TargetTupoksi,
		Sequence:      payload.Sequence,
		Description:   payload.Description,
		CreatedBy:     userSession,
	}

	if err := config.db.Create(&create).Error; err != nil {
		utils.ResponseError(w, http.StatusBadRequest, "Invalid body")
		return
	}

	utils.ResponseOk(w, create)
}

func (config *ConfigDB) putTupoksiJabatan(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	params := mux.Vars(r)
	ctx := r.Context().Value("user")
	sessionUser := ctx.(*jwt.Token).Claims.(jwt.MapClaims)
	decoder := json.NewDecoder(r.Body)
	payload := models.TupoksiJabatan{}
	if err := decoder.Decode(&payload); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	strSession := sessionUser["email"]
	userSession := strSession.(string)
	// check id jabatan
	if err := config.db.Where("ID = ?", params["id"]).Find(&models.TupoksiJabatan{}).Error; err != nil {
		utils.ResponseError(w, http.StatusNotFound, "ID Not Found")
		return
	}

	var jabatan models.Jabatan
	if err := config.db.Where("ID = ?", payload.JabatanID).Find(&jabatan).Error; err != nil {
		utils.ResponseError(w, http.StatusNotFound, "JabatanID ID Not Found")
		return
	}

	update := models.TupoksiJabatan{
		Jabatan:       jabatan,
		JabatanID:     jabatan.ID,
		NameTupoksi:   payload.NameTupoksi,
		TargetTupoksi: payload.TargetTupoksi,
		Sequence:      payload.Sequence,
		Description:   payload.Description,
		UpdatedBy:     userSession,
	}

	if err := config.db.Model(&payload).Where("ID = ?", params["id"]).Update(&update).Error; err != nil {
		utils.ResponseError(w, http.StatusBadRequest, "Invalid body")
		return
	}

	utils.ResponseOk(w, update)
}

func (config *ConfigDB) detailTupoksiJabatan(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	params := mux.Vars(r)
	var response models.TupoksiJabatan
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

func (config *ConfigDB) deleteTupoksiJabatan(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	params := mux.Vars(r)
	if err := config.db.Exec("DELETE FROM tupoksi_jabatans WHERE id = ?", params["id"]).Error; err != nil {
		utils.ResponseError(w, http.StatusBadRequest, "Data Not Found")
		return
	}

	// config.db.Model(&payload).Where("ID = ?", params["id"]).Delete(&payload)
	response := "Data Berhasil Di Hapus"
	result := models.ResultsData{
		Status:  http.StatusOK,
		Success: true,
		Results: response,
	}
	utils.ResponseOk(w, result)
}

func getDetailTupoksiByte(config *ConfigDB, id string) ([]byte, error) {
	var response models.TupoksiJabatan
	result := config.db.Where("ID = ?", id).Find(&response)
	if result.Error != nil {
		result = nil
	}
	bytes, _ := json.Marshal(result)
	return bytes, nil
}
