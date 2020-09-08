package models

type ResultsData struct {
	Status  int         `json:"status"`
	Success bool        `json:"success"`
	Message string      `json:"message"`
	Results interface{} `json:"results"`
	Meta    interface{} `json:"_meta"`
}

type MetaData struct {
	TotalCount  int `json:"totalCount"`
	TotalPage   int `json:"totalPage"`
	CurrentPage int `json:"currentPage"`
	PerPage     int `json:"perPage"`
}
