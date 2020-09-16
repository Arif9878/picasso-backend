import os, xlsxwriter, io
from datetime import datetime, timedelta
from xlsxwriter.utility import xl_range

from os.path import join, dirname, exists
from dotenv import load_dotenv
from flask import Flask, send_file, request
from flask_sqlalchemy import SQLAlchemy
from pymongo import MongoClient
from utils import monthlist_short, isWeekDay, getHours, getInformation, queryAccount

app = Flask(__name__)

dotenv_path = ''
if exists(join(dirname(__file__), '../../.env')):
    dotenv_path = join(dirname(__file__), '../../.env')
else:
    dotenv_path = join(dirname(__file__), '../.env')

load_dotenv(dotenv_path)

mongoURI = 'mongodb://{dbhost}:{dbport}/'.format(
    dbhost=os.environ.get('DB_MONGO_HOST'),
    dbport=os.environ.get('DB_MONGO_PORT')
)
mongoClient = MongoClient(mongoURI)

postgreURI = 'postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}:{dbport}/{dbname}'.format(
    dbuser=os.environ.get('DB_USER_AUTH'),
    dbpass=os.environ.get('DB_PASSWORD_AUTH'),
    dbhost=os.environ.get('POSTGRESQL_HOST'),
    dbport=os.environ.get('POSTGRESQL_PORT'),
    dbname=os.environ.get('DB_NAME_AUTH')
)

app.config.update(
    SQLALCHEMY_DATABASE_URI=postgreURI,
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

db = SQLAlchemy(app)

@app.route('/api/export-excel/')
def exportExcel():
    divisi = request.args.get('divisi')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    dates = [start_date, end_date]

    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    bold = workbook.add_format({'bold': True})

    worksheet.write('A1', 'Nama Divisi')

    listDate = list(monthlist_short(dates))

    # Write some numbers, with row/column notation.
    worksheet.set_column(0, 0, 20)
    worksheet.write(1, 0, "Tanggal")
    worksheet.write(2, 0, "Nama Pegawai")

    merge_red_format = workbook.add_format({
        'bg_color': '#FFC7CE',
        'align': 'center',
        'valign': 'vcenter'})
    merge_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter'})
    red_format = workbook.add_format({'bg_color': '#FFC7CE'})
    totalListDate = len(listDate)
    index = 0
    for idx in range(0, totalListDate * 2):
        idx += 1
        if (idx % 2 != 0):
            index += 1
            worksheet.set_column(2, idx, 15)
            if isWeekDay(listDate[index - 1]) is False:
                worksheet.write(2, idx, 'Jumlah Jam Kerja', red_format)
                worksheet.write(2, idx + 1, 'Keterangan', red_format)
                worksheet.merge_range(1, idx, 1, idx + 1, listDate[index-1], merge_red_format)
            else:
                worksheet.write(2, idx, 'Jumlah Jam Kerja')
                worksheet.write(2, idx + 1, 'Keterangan')
                worksheet.merge_range(1, idx, 1, idx + 1, listDate[index - 1],
                                      merge_format)

    worksheet.merge_range(1, (totalListDate * 2) + 1, 2,
                          (totalListDate * 2) + 1, "TOTAL", merge_format)
    worksheet.merge_range(1, (totalListDate * 2) + 2, 2,
                          (totalListDate * 2) + 2, "TTD", merge_format)
    query = queryAccount(divisi=divisi)
    result = db.session.execute(query)
    divisiName = ''
    indexNamePegawai = 2
    for i in result:
        indexNamePegawai += 1
        fullname = i[1]+" "+i[2]
        divisiName = i[3]
        worksheet.write(indexNamePegawai, 0, fullname)
        indexDate = 0
        for b in range(0, totalListDate * 2):
            b += 1
            if (b % 2 != 0):
                indexDate += 1
                cell_range = xl_range(indexNamePegawai, 1, indexNamePegawai, b)
                formula = '=SUM(%s)' % cell_range
                hour = getHours(mongoClient, i[0], listDate[indexDate - 1])
                information = getInformation(mongoClient, i[0], listDate[indexDate - 1])
                if isWeekDay(listDate[indexDate - 1]) is False and hour == 0:
                    worksheet.merge_range(indexNamePegawai, b,
                                          indexNamePegawai, b + 1, 'Libur',
                                          merge_red_format)
                else:
                    worksheet.write(indexNamePegawai, b, hour)
                    worksheet.write(indexNamePegawai, b + 1, information)
                worksheet.write_formula(indexNamePegawai,
                                        (totalListDate * 2) + 1, formula)

    worksheet.write('B1', divisiName, bold)

    nameFile = divisiName.split(" ")
    nameFile = "".join(divisiName)
    workbook.close()
    output.seek(0)
    return send_file(output, attachment_filename="%s.xlsx" % nameFile, as_attachment=True)

port = os.environ.get('EXPORT_EXCEL_PORT', 80)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(port))
