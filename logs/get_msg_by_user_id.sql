SELECT 
	user.user_name,
	channel.channel_name,
	message.content,
	message.message_id,
	time
	FROM message
	INNER JOIN user on user.user_id = message.user_id
	INNER JOIN channel on channel.channel_id = message.channel_id 
	INNER JOIN category on channel.category_id = category.category_id
	INNER JOIN server on category.server_id = server.server_id
	WHERE 
		server.server_id = 679614550286663721 
		AND
		user.user_id = 478603062332882955
