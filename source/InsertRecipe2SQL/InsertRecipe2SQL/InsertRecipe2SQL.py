# -*- coding: utf-8 -*-
import MySQLdb
import xlrd
import os.path

if __name__ == "__main__":

    evmpath = "..\\..\\..\\"
    SentenceDBFile = evmpath + "db\\MixedDBwithStep.xlsx"
    userName = ''
    password = ''
    SchemaName = 'cooking_task'
    tableName = 'mixing_task'

    connect = ""

    if os.path.exists(SentenceDBFile):
        RecipeDB = xlrd.open_workbook(SentenceDBFile)
        connect = MySQLdb.connect(host='localhost', port=3306, user=userName, passwd=password, db=SchemaName, charset='utf8')
        
    StatisticsSheet = RecipeDB.sheet_by_index(1)
    print 'sheet name is ' + RecipeDB.sheet_by_index(1).name
    nrows = StatisticsSheet.nrows - 2

    for row in range(nrows):
        task_id = int(StatisticsSheet.cell_value(row + 2, 0))
        tmp_recipe_id = StatisticsSheet.cell_value(row + 2, 1)
        tmp = []
        tmp = tmp_recipe_id.split('\'')
        recipe_id = tmp[0]
        sentence = StatisticsSheet.cell_value(row + 2, 4)
        step = int(StatisticsSheet.cell_value(row + 2, 3))
        materials = ""
        
        Materials = []
        for Mcol in range(5, 13):
            if StatisticsSheet.cell_type(row + 2, Mcol) is 1:
                materials += StatisticsSheet.cell_value(row + 2, Mcol) + '\t'
        materials = materials[:-1]

        # print type(recipe_id), type(sentence), type(materials)
        print '%s, %s, %s, %s, %s' % (task_id, recipe_id, step, sentence, materials)
        valueStrings ="('" + recipe_id + "'," + str(task_id) + ", " + str(step) + ",'" + sentence + "', '" + materials + "')"
        
        cursor = connect.cursor()

        sql = "INSERT INTO " + SchemaName + "." + tableName +" (recipe_id, task_id, step, sentence, materials) VALUES " + valueStrings
        print sql
        cursor.execute(sql)
        
    connect.commit()
    cursor.close()
    connect.close()