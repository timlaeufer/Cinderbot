SELECT  
	user.user_name as "name",
	COUNT(*) as amount,
	COUNT(*)/53186.0*100 as "percentage"
	from message
	INNER JOIN channel on channel.channel_id = message.channel_id 
	INNER JOIN user on user.user_id = message.user_id
	INNER JOIN category on channel.category_id = category.category_id
	INNER JOIN server on category.server_id = server.server_id
	WHERE server.server_id = 679614550286663721
		and message.server_id = 679614550286663721
	GROUP BY message.user_id
	ORDER BY amount desc