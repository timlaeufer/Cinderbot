SELECT 
	user.user_name,
	channel.channel_name,
	edits.old_content,
	edits.new_content,
	edits.channel_name,
	edits.category_name,
	edits.time,
	edits.message_id
	FROM edits
	INNER JOIN user on user.user_id = message.user_id
	INNER JOIN channel on channel.channel_id = message.channel_id 
	INNER JOIN category on channel.category_id = category.category_id
	INNER JOIN server on category.server_id = server.server_id
	INNER JOIN message on message.message_id = edits.message_id
	WHERE 
		server.server_id = 679614550286663721 
		AND
		user.user_id = 314135917604503553
	ORDER BY edits.time desc
