const DAILY_AMOUNT = 100;

exports.handler = async (event) => {
    const headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Content-Type': 'application/json'
    };

    if (event.httpMethod === 'OPTIONS') {
        return { statusCode: 204, headers, body: '' };
    }

    try {
        const { Blobs } = require('@netlify/blobs');
        const { userId, username } = JSON.parse(event.body);

        if (!userId) {
            return {
                statusCode: 400,
                headers,
                body: JSON.stringify({ 
                    success: false, 
                    message: 'ID não fornecido' 
                })
            };
        }

        // Conectar ao store
        const userStore = Blobs.store('users');
        
        // Buscar usuário existente
        let user = await userStore.get(userId, { type: 'json' });
        const now = new Date();

        if (!user) {
            // Criar novo usuário
            user = {
                user_id: userId,
                username: username || 'Usuário',
                balance: 0,
                last_daily: null,
                total_earned: 0,
                daily_streak: 0,
                created_at: now.toISOString()
            };
        }

        // Verificar se já resgatou hoje
        if (user.last_daily) {
            const lastDaily = new Date(user.last_daily);
            const timeDiff = (now - lastDaily) / 1000; // segundos
            
            if (timeDiff < 86400) { // 24h em segundos
                return {
                    statusCode: 200,
                    headers,
                    body: JSON.stringify({
                        success: false,
                        message: '⏰ Você já resgatou hoje!',
                        timeLeft: 86400 - timeDiff
                    })
                };
            }
        }

        // Calcular streak
        let streak = 1;
        if (user.last_daily) {
            const last = new Date(user.last_daily);
            const hoursSince = (now - last) / (1000 * 60 * 60);
            streak = hoursSince < 48 ? (user.daily_streak || 0) + 1 : 1;
        }

        // Calcular bônus (até 70%)
        const bonus = 1 + (Math.min(streak, 7) * 0.1);
        const amount = Math.floor(DAILY_AMOUNT * bonus);

        // Atualizar usuário
        const updatedUser = {
            ...user,
            username: username || user.username,
            balance: (user.balance || 0) + amount,
            last_daily: now.toISOString(),
            daily_streak: streak,
            total_earned: (user.total_earned || 0) + amount
        };

        // Salvar no Blobs
        await userStore.set(userId, JSON.stringify(updatedUser));

        return {
            statusCode: 200,
            headers,
            body: JSON.stringify({
                success: true,
                amount,
                streak,
                newBalance: updatedUser.balance,
                message: `🎉 Ganhou ${amount} moedas! Streak: ${streak}`
            })
        };

    } catch (error) {
        console.error('Erro claim:', error);
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({ 
                success: false, 
                message: 'Erro ao processar resgate' 
            })
        };
    }
};
