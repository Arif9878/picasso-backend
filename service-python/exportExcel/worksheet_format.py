import xlsxwriter
from xlsxwriter.utility import xl_range
from utils import isWeekDay, getHours, getInformation, getTimePresence

def exportExcelFormatHorizontal(mongoClient, output, listDate ,result):
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    bold = workbook.add_format({'bold': True})

    worksheet.write('A1', 'Nama Divisi')

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
    divisiName = ''
    indexNamePegawai = 2
    for i in result:
        indexNamePegawai += 1
        fullname = i[1]
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
    return output, nameFile

def exportExcelFormatVertical(mongoClient, output, listDate ,result):
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    bold = workbook.add_format({'bold': True})
    yellow_format = workbook.add_format({'bg_color': '#ffdb47'})

    worksheet.set_column(0, 20, 15)
    worksheet.write('A1', 'No', yellow_format)
    worksheet.write('B1', 'Nama', yellow_format)
    worksheet.write('C1', 'Tanggal', yellow_format)
    worksheet.write('D1', 'Scan Masuk', yellow_format)
    worksheet.write('E1', 'Scan Keluar', yellow_format)
    worksheet.write('F1', 'Jumlah Jam Kerja', yellow_format)
    worksheet.write('G1', 'Keterangan', yellow_format)
    worksheet.write('H1', 'Total Jumlah Jam Kerja', yellow_format)
    worksheet.write('I1', 'TTD', yellow_format)

    lengthDate = len(listDate)
    indexPegawai = 0
    indexContents = 0
    indexLengthDate = 1
    for i in result:
        indexPegawai += 1
        for d in listDate:
            indexContents += 1
            presence = getTimePresence(mongoClient, i[0], d)
            hour = getHours(mongoClient, i[0], d)
            information = getInformation(mongoClient, i[0], d)
            worksheet.write(indexContents, 0, indexPegawai)
            worksheet.write(indexContents, 1, i[1])
            worksheet.write(indexContents, 2, d)
            worksheet.write(indexContents, 3, presence[0])
            worksheet.write(indexContents, 4, presence[1])
            worksheet.write(indexContents, 5, hour)
            worksheet.write(indexContents, 6, information)
        if indexPegawai > 1:
            indexLengthDate += lengthDate
        cell_range = xl_range(indexLengthDate, 5, indexPegawai*lengthDate, 5)
        formula = '=SUM(%s)' % cell_range
        worksheet.merge_range(indexLengthDate, 7, indexPegawai*lengthDate, 7, formula)
        worksheet.merge_range(indexLengthDate, 8, indexPegawai*lengthDate, 8, '')

    workbook.close()
    return output
