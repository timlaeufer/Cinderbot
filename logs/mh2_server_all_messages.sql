SELECT 
	user_name as "user name", 
	user_nick as "nickname",
	content as "content", 
	channel_name as "Channel", 
	category_name as "Category",
	server_name as "Server",
	user.user_id as "user id",
	server.server_id as "server id",
	category.category_id as "category id",
	channel.channel_id as "channel id",
	message.message_id as "message id",
	time from user	
	INNER JOIN channel on channel.channel_id = message.channel_id 
	INNER JOIN message on user.user_id = message.user_id
	INNER JOIN category on channel.category_id = category.category_id
	INNER JOIN server on category.server_id = server.server_id
	WHERE server.server_id = 679614550286663721
	ORDER BY time asc
	