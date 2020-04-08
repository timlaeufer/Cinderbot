SELECT  
	user.user_name as "name",
	COUNT(*) as amount,
	user.user_id
	from message
	INNER JOIN channel on channel.channel_id = message.channel_id 
	INNER JOIN user on user.user_id = message.user_id
	INNER JOIN category on channel.category_id = category.category_id
	INNER JOIN server on category.server_id = server.server_id
	GROUP BY message.user_id
	ORDER BY amount desc