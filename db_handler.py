# -*- coding: utf-8 -*-
"""
Created on Tue Apr 07 14:25:34 2020

@author: Timmitim (Tim Laeufer)
"""

import discord
import sqlite3

class db_handler:
    STR_SERVER = 'server'
    STR_USER = 'user'
    STR_CHANNEL = 'channel'
    STR_CATEGORY = 'category'
    STR_MESSAGE = 'message'
    STR_EDITS = 'edits'
    STR_DELETES = 'deletes'

    def log(self, rel_path, message):
        conn = sqlite3.connect('logs/messages.db')
        c = conn.cursor()
        """
        Flow:

        Check if DM
            True
                Check if user exists
                    True
                        user_info = ...
                    False
                        create user
                        user_info = ...
                Check if channel exists
                    True
                        channel_info = ...
                    False
                        create channel
                        channel_info = ...
                server_info = None/0
                category_info = None/0
            False
                Check if server exists
                    True
                        server_info = ...
                    False
                        create_server
                        server_info = ...
                Check if user exists
                    True
                        user_info = ...
                    False
                        create user
                        user_info = ...
                Check if category_exists
                    True
                        category_info = ...
                    False
                        create category
                        category_info = ...
                Check if channel exists
                    True
                        channel_info = ...
                    False
                        create_channel
                        channel_info = ...

        create_message
        """
        ins = False
        #Check if DM
        try:
            cat = message.channel.category
            is_dm = False
        except AttributeError:
            is_dm = True

        if(is_dm):
            self.insert_user(c, message.author)
            self.insert_channel(c, message.channel, is_dm = True)
        else:
            #is not a dm:
            self.insert_user(c, message.author)
            self.insert_server(c, message.guild)
            try:
                self.insert_category(c, message.channel.category)
            except:
                pass
            if(message.guild.id == 679614550286663721):
                ins = True
            self.insert_channel(c, message.channel)
            
        if(ins):
            self.insert_message(cursor = c, message_obj = message)
        conn.commit()
        conn.close()

    def log_join(self, member_obj, amount_users):
        conn = sqlite3.connect('logs/messages.db')
        c = conn.cursor()

        query = 'INSERT INTO join (join_id,amount_now) '
        query += 'VALUES ({mem_id},{amount});'

        c.execute(query.format(
            mem_id = member_obj.id,
            amount = amount_users))

        conn.commit()
        conn.close()

    def log_edit(self, rel_path, message_before, message):
        self.log_msg_edit(rel_path, message_before, message)

    def log_msg_edit(self, rel_path, message_before, message_obj):
        conn = sqlite3.connect(rel_path)
        c = conn.cursor()

        try: #add message, if not in db
            self.insert_message(c, message_before)
        except:
            pass
        
        try:
            cat = message_obj.channel.category.name
            cat_id = message_obj.channel.category.id
        except AttributeError:
            cat = 'None'
            cat_id = 0
        try:
            auth_name = message_obj.author.nick
        except AttributeError:
            auth_name = message_obj.author.name
        query = 'INSERT INTO {table} '
        query += '(message_id,channel_id,user_id,user_nick,time,old_content,new_content,server_id,category_id,channel_name,category_name) '
        query += 'VALUES ({msg_id},{ch_id},{u_id},"{u_nick}","{time}","{old_content}","{content}",{s_id},{cat_id},"{channel_name}","{category_name}");'
        query = query.format(
            table = self.STR_EDITS,
            msg_id = message_obj.id,
            ch_id = message_obj.channel.id,
            u_id = message_obj.author.id,
            u_nick = auth_name,
            time = str(message_obj.created_at) + 'UTC',
            old_content = message_before.content.replace('"', '/'),
            content = message_obj.clean_content.replace('"', '/'),
            s_id = message_obj.guild.id,
            cat_id = cat_id,
            channel_name = message_obj.channel.name,
            category_name = cat)
        c.execute(query)
        conn.commit()
        conn.close()

    def log_delete(self, rel_path, message):
        self.log_msg_delete(rel_path, message)

    def log_msg_delete(self, rel_path, message_obj):
        conn = sqlite3.connect(rel_path)
        cursor = conn.cursor()

        try:
            nick = message_obj.author.nick
        except AttributeError:
            nick = message_obj.author.name


        try: #on server, with category
            query = 'INSERT INTO {table} '
            query += '(message_id,channel_id,user_id,user_nick,time,content,server_id,category_id,channel_name,category_name) '
            query += 'VALUES ({msg_id},{ch_id},{u_id},"{u_nick}","{time}","{content}", {s_id},{cat_id},"{ch_name}","{cat_name}");'
            query = query.format(
                table = self.STR_DELETES,
                msg_id = message_obj.id,
                ch_id = message_obj.channel.id,
                u_id = message_obj.author.id,
                u_nick = nick,
                time = str(message_obj.created_at) + 'UTC',
                content = message_obj.clean_content.replace('"', '/'),
                s_id = message_obj.guild.id,
                cat_id = message_obj.channel.category.id,
                ch_name = message_obj.channel.name,
                cat_name = message_obj.channel.category.name)
        except AttributeError:
            try:#on server, no category
                query = 'INSERT INTO {table} '
                query += '(message_id,channel_id,user_id,user_nick,time,content,server_id,channel_name) '
                query += 'VALUES ({msg_id},{ch_id},{u_id},"{u_nick}","{time}","{content}", {s_id},"{ch_name}");'
                query = query.format(
                    table = self.STR_DELETES,
                    msg_id = message_obj.id,
                    ch_id = message_obj.channel.id,
                    u_id = message_obj.author.id,
                    u_nick = nick,
                    time = str(message_obj.created_at) + 'UTC',
                    content = message_obj.clean_content.replace('"', '/'),
                    s_id = message_obj.guild.id,
                    ch_name = message_obj.channel.name)
            except AttributeError: #not on server
                query = 'INSERT INTO {table} '
                query += '(message_id,channel_id,user_id,user_nick,time,content) '
                query += 'VALUES ({msg_id},{ch_id},{u_id},"{u_nick}","{time}","{content}");'
                query = query.format(
                    table = self.STR_DELETES,
                    msg_id = message_obj.id,
                    ch_id = message_obj.channel.id,
                    u_id = message_obj.author.id,
                    u_nick = nick,
                    time = str(message_obj.created_at) + 'UTC',
                    content = message_obj.clean_content.replace('"', '/'))
        cursor.execute(query)
        conn.commit()
        conn.close()
        
        

    def exists_in_db(self, cursor, table, element_id):
        # SELECT EXISTS(SELECT 1 FROM myTbl WHERE u_tag="tag");
        c = cursor

        query = 'SELECT EXISTS(SELECT 1 FROM {table} WHERE {table}_id = {row_id});'
        query = query.format(
            table = table,
            row_id = element_id)
        c.execute(query)

        if(c.fetchone()[0] == 0):
            return False
        else:
            return True

    def insert_user(self, cursor, author_obj):

        if(self.exists_in_db(cursor, self.STR_USER, author_obj.id)):
            return cursor

        query = 'INSERT INTO {table} (user_id,user_name) VALUES ({u_id},"{u_name}");'
        query = query.format(
            table = self.STR_USER,
            u_id = author_obj.id,
            u_name = author_obj.name)
        cursor.execute(query)
        return cursor

    def insert_server(self, cursor, server_obj):

        if(self.exists_in_db(cursor, self.STR_SERVER, server_obj.id)):
            return cursor

        query = 'INSERT INTO {table} (server_id,server_name) VALUES ({s_id},"{s_name}");'
        query = query.format(
            table = self.STR_SERVER,
            s_id = server_obj.id,
            s_name = server_obj.name)
        cursor.execute(query)
        return cursor

    def insert_category(self, cursor, category_obj):

        if(self.exists_in_db(cursor, self.STR_CATEGORY, category_obj.id)):
            return cursor

        query = 'INSERT INTO {table} (category_id,category_name,server_id) VALUES ({c_id},"{c_name}",{s_id});'
        query = query.format(
            table = self.STR_CATEGORY,
            c_id = category_obj.id,
            c_name = category_obj.name,
            s_id = category_obj.guild.id)
        cursor.execute(query)
        return cursor

    def insert_channel(self, cursor, channel_obj, is_dm = False):

        if(self.exists_in_db(cursor, self.STR_CHANNEL, channel_obj.id)):
            return cursor

        try:
            cat = channel_obj.category
            has_category = True
        except AttributeError:
            has_category = False

        if(is_dm):
            pass
        else:
            if(has_category):
                query = 'INSERT INTO {table} (channel_id,channel_name,category_id,server_id) VALUES '
                query += '({c_id},"{c_name}",{cat_id},{s_id});'
                query = query.format(
                    table = self.STR_CHANNEL,
                    c_id = channel_obj.id,
                    c_name = channel_obj.name,
                    cat_id = channel_obj.category.id,
                    s_id = channel_obj.guild.id)
            else:
                query = 'INSERT INTO {table} (channel_id,channel_name,category_id,server_id) VALUES '
                query += '({c_id},"{c_name}",{cat_id},{s_id});'
                query = query.format(
                    table = self.STR_CHANNEL,
                    c_id = channel_obj.id,
                    c_name = channel_obj.name,
                    cat_id = 0,
                    s_id = channel_obj.guild.id)
            cursor.execute(query)
            return cursor

    def insert_message(self, cursor, message_obj):

        try:
            nick = message_obj.author.nick
        except AttributeError:
            nick = message_obj.author.name


        try: #on server, with category
            query = 'INSERT INTO {table} '
            query += '(message_id,channel_id,user_id,user_nick,time,content,server_id,category_id,channel_name,category_name) '
            query += 'VALUES ({msg_id},{ch_id},{u_id},"{u_nick}","{time}","{content}", {s_id},{cat_id},"{ch_name}","{cat_name}");'
            query = query.format(
                table = self.STR_MESSAGE,
                msg_id = message_obj.id,
                ch_id = message_obj.channel.id,
                u_id = message_obj.author.id,
                u_nick = nick,
                time = str(message_obj.created_at) + 'UTC',
                content = message_obj.clean_content.replace('"', '/'),
                s_id = message_obj.guild.id,
                cat_id = message_obj.channel.category.id,
                ch_name = message_obj.channel.name,
                cat_name = message_obj.channel.category.name)
        except AttributeError:
            try:#on server, no category
                query = 'INSERT INTO {table} '
                query += '(message_id,channel_id,user_id,user_nick,time,content,server_id,channel_name) '
                query += 'VALUES ({msg_id},{ch_id},{u_id},"{u_nick}","{time}","{content}", {s_id},"{ch_name}");'
                query = query.format(
                    table = self.STR_MESSAGE,
                    msg_id = message_obj.id,
                    ch_id = message_obj.channel.id,
                    u_id = message_obj.author.id,
                    u_nick = nick,
                    time = str(message_obj.created_at) + 'UTC',
                    content = message_obj.clean_content.replace('"', '/'),
                    s_id = message_obj.guild.id,
                    ch_name = message_obj.channel.name)
            except AttributeError: #not on server
                query = 'INSERT INTO {table} '
                query += '(message_id,channel_id,user_id,user_nick,time,content) '
                query += 'VALUES ({msg_id},{ch_id},{u_id},"{u_nick}","{time}","{content}");'
                query = query.format(
                    table = self.STR_MESSAGE,
                    msg_id = message_obj.id,
                    ch_id = message_obj.channel.id,
                    u_id = message_obj.author.id,
                    u_nick = nick,
                    time = str(message_obj.created_at) + 'UTC',
                    content = message_obj.clean_content.replace('"', '/'))
        cursor.execute(query)
        return cursor


    def fetch_sql_rows(self, db, sql):
        conn = sqlite3.connect(db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        lis = cursor.execute(sql).fetchall()
        conn.close()
        return lis
        

        
    
