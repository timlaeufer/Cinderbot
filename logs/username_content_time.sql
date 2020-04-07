SELECT 
	user_name as "user", 
	user_nick as "nickname",
	content as "content", 
	channel_name as "Channel", 
	category_name as "Category",
	server_name as "Server",
	time from user 
	INNER JOIN channel on channel.channel_id = message.channel_id 
	INNER JOIN message on user.user_id = message.user_id
	INNER JOIN category on channel.category_id = category.category_id
	INNER JOIN server on category.server_id = server.server_id
	ORDER BY time asc
	