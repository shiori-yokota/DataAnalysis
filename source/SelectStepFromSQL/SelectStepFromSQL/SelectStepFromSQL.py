# -*- coding: utf-8 -*-
import MySQLdb
import xlrd
import os.path

if __name__ == "__main__":
	
	evmpath = "..\\..\\..\\"
	SentenceDBFile = evmpath + "db\\MixedDB.xlsx"
	userName = "root"
	password = 'inamuralab'
	SchemaName = 'cookpad_data'
	tableName = 'steps'

	connect = ""

	if os.path.exists(SentenceDBFile):
		RecipeDB = xlrd.open_workbook(SentenceDBFile)
		connect = MySQLdb.connect(host='localhost', port=3306, user=userName, passwd=password, db=SchemaName, charset='utf8')

	StatisticsSheet = RecipeDB.sheet_by_index(1)
	print 'sheet name is ' + RecipeDB.sheet_by_index(1).name
	nrows = StatisticsSheet.nrows - 2

	for row in range(nrows):
		no = StatisticsSheet.cell_value(row + 2, 0)
		tmp_recipe_id = StatisticsSheet.cell_value(row + 2, 1)
		tmp = []
		tmp = tmp_recipe_id.split('\'')
		recipe_id = tmp[0]
		#print recipe_id
		sentence = StatisticsSheet.cell_value(row + 2, 3)
		#print sentence

		cursor = connect.cursor()

		sql = "SELECT * FROM " + SchemaName + "." + tableName + " WHERE recipe_id='" + recipe_id + "' AND memo LIKE '%" + sentence + "%'"
		#print sql
		cursor.execute(sql)

		result = cursor.fetchall()

		for row in result:
			print "==== HIT ===="
			print "No. " + str(no)
			print "position " + str(row[1])
			print "memo " + row[2]
			print "============="