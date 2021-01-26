from django.db import (
    models, connection)


class MenuManager(models.Manager):

    def list(self, menu_type=None):
        """
            Query untuk menu
        """
        cursor = connection.cursor()

        query = """
            SELECT
                m.id,
                m.title,
                m.icon,
                m.seq,
                CASE 
                    WHEN (SELECT COUNT(*) FROM menu_menu m2 WHERE m.id = m2.parent_id AND m2.enable is TRUE AND m2.menu_type_id = %s) = 0
                    THEN m.furl
                    ELSE null
                END AS to,
                CASE 
                    WHEN (SELECT COUNT(*) FROM menu_menu m2 WHERE m.id = m2.parent_id AND m2.enable is TRUE AND m2.menu_type_id = %s) > 0
                    THEN m.furl
                    ELSE null 
                END AS group,
                (SELECT ARRAY(
                    SELECT
                        json_build_object(
                            'id', m2.id,
                            'title', m2.title,
                            'seq', m2.seq,
                            'to', m2.furl
                        )
                    FROM
                        menu_menu m2
                    WHERE
                        m.id = m2.parent_id
                        AND enable is TRUE
        """ % (menu_type, menu_type)

        query += "AND m2.menu_type_id = %s" % menu_type
        query += """
                    ORDER BY
                        m2.seq ASC
                )) children
            FROM
                menu_menu m
            WHERE
                parent_id is NULL
                AND menu_type_id = %s
                AND enable is TRUE
        """ % menu_type

        query += "ORDER BY m.seq ASC"

        try:
            cursor.execute(query)

            columns = [col[0] for col in cursor.description]

            return [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]
        finally:
            cursor.close()

    def parent(
            self,
            limit=None,
            offset=None):
        """
            Query untuk menu
        """
        cursor = connection.cursor()

        query = """
            SELECT
            title,
            furl as to
            FROM menu_menu
            WHERE enable = 1
            AND parentcode = '0'
        """

        if limit is not None and offset is not None:
            limitQuery = "LIMIT %s OFFSET %s" % (limit, offset)
            query = query + limitQuery

        try:
            cursor.execute(query)

            columns = [col[0] for col in cursor.description]

            return [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]
        finally:
            cursor.close()
