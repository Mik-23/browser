        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        body {

            margin: 0;
            padding: 20px;
            background-color: rgba(0, 0, 45, 11);
            overflow-x: hidden;
        }


        h1 {
            color: #D9FFFD;
        }

        h2 {
            text-align: left;
            color: #FFFAFA;

        }

        .messenger {
            width: 100%;
            max-width: 1400px;
            height: 90vh;
            background: #0E1621;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-radius: 36px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.75), inset 0 1px 2px rgba(255, 255, 255, 0.08);
            display: flex;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        .sidebar {
            width: 360px;
            background: #06002E
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-right: 1px solid rgba(255, 255, 255, 0.05);
            display: flex;
            flex-direction: column;
            padding: 24px 16px;
            gap: 20px;
        }

        /* шапка sidebar */
        .sidebar-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 8px;
        }

        .main-chat {
            flex: 1;
            overflow: auto;
            display: flex;
            flex-direction: column;
            background: #0E1621;
            position: relative;
        }

        .sent {
            bottom: 80px;
            right: 550px;
            max-width: 30px; /* чтобы не превращался в огромный */
            box-sizing: border-box; /* чтобы padding не влияли на ширину */
            z-index: 9999; /* чтобы не перекрывалось чем-то */
            width: calc(100% - 40px);
            font-size: 14px;
        }

        .mediaIcons {
            bottom: 80px;
            right: 470px;
            max-width: 30px; /* чтобы не превращался в огромный */
            box-sizing: border-box; /* чтобы padding не влияли на ширину */
            z-index: 9999; /* чтобы не перекрывалось чем-то */
            width: calc(100% - 40px);
            font-size: 14px;
        }

        .messages {
            max-height: 400px;
            overflow: auto;
            border: 1px solid #ccc;
            padding: 10px;
            margin-bottom: 15px;
        }
        .message {
            margin-bottom: 10px;
            max-height: 400px;
            overflow: auto;
            border: 1px solid #ccc;
            padding: 10px;
        }
        .message .sender {
            font-weight: bold;
        }
        .form-group{
             width: 90%;
             display: flex;
             background: rgba(255, 255, 255, 0.06);
             border: 1px solid rgba(255, 255, 255, 0.05);
             border-radius: 40px;
             justify-content: space-between;
             position: relative; /* или static */
             padding: 0 10px;
             box-sizing: border-box;
        }

        .input-panel {
            backdrop-filter: blur(16px);
            border-top: 1px solid rgba(255, 255, 255, 0.04);
            padding: 18px 28px;
            display: flex;
            gap: 12px;
            align-items: center;
        }

        .input-wrapper {
            flex: 1;
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 40px;
            padding: 4px 4px 4px 22px;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: 0.15s;
        }

        .input-wrapper input {
            background: transparent;
            border: none;
            padding: 14px 0;
            color: white;
            font-size: 14px;
            outline: none;
            width: 100%;
        }


        .input-wrapper text {
            font-size: 10px;
        }

        .form-group input {
            background: transparent;
            border: none;
            padding: 14px 0;
            color: white;
            font-size: 14px;
            outline: none;
            width: 100%;
        }

        .chat-align {
            text-align: center; /* Выравнивание текста влево */
        }

        .message-align {
            margin-top: -100px; /* Выравнивание текста влево */

        }

        .user-list {
            background-color: #3a3a3a;
            max-width: 170px;
            margin: 0px 170px
        }

        .user-list li {
           list-style-type: none;
           margin-left: auto;
           color: white;
           line-height: 1.9
        }

        .files-container {
            display: none;
            position: absolute;
            bottom: 80px;
            right: 80px;
            background: #17212b;
            border-radius: 16px;
            padding: 8px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.5);
            z-index: 100;
        }

        .files-container img{
            width: 25px; /* Установите желаемую ширину */
            height: 25px; /* Установите желаемую высоту */

        }

        .message-list {
            overflow-y: auto;
        }

        .message-message-list li {
            list-style-type: none;
            text-align: left; /* Выравнивание текста вправо */
            font-size: 20px;
            overflow-y: auto;
            color: #E0FFFF;
            border: none; /* Граница вокруг сообщения */
            border-radius: 40px; /* Закругление углов */
            padding: 10px;
            background-color: #3a3a3a;
            max-width: 600px; /* Максимальная ширина сообщения */
            width: 100%;

        }

        .message-message-list p {
            font-size: 10px;


        }


        #messageContent {
            width: calc(100% - 40px);
            max-width: 400px; /* чтобы не превращался в огромный */
            box-sizing: border-box; /* чтобы padding не влияли на ширину */
            z-index: 9999; /* чтобы не перекрывалось чем-то */

        }

        .chat-list ul{
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 8px;

        }

        .chat-list li {
            background-color: #3a3a3a;
            font-size: 18px;
            border-radius: 12px;
            list-style-type: none;
            color: #fff;
            display: block;
        }


        .chat-list p {
            font-size: 19px;
            list-style-type: none;
            color: #C0C0C0;
        }

        .logout-container button{
            margin-right: 600px;
        }

        .files-container label {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 4px 2px;
            cursor: pointer;
            border-radius: 8px;
            transition: 0.15s;
        }

        .files-container p {
            font-size: 17px;
            color: #D9FFFD;
        }

        .files-container p:hover {
            color: #02D6ED;
        }


        button {
            width: 70px; /* Уменьшено для кнопки отправки */
            padding: 10px;
            background-color: #2c2c2c;
            color: #D9FFFD;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        .btn:hover {
            color: #02D6ED;
            background: #08003B
        }

        .out-chat svg {
            width: 30px;
            height: 30px;
            fill: none;
            stroke-width: 2;
        }

        .out-chat {
            background: none;
            width: 45px;
            height: 45px;
        }

         .mediaIcons svg {
            width: 24px;
            height: 24px;
            fill: none;
            stroke: #545454;
            stroke-width: 2;
        }

        .mediaIcons {
            background: transparent;
            border: none;
            cursor: pointer;
            max-width: 45px;
            height: 45px;
            padding: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            transition: 0.15s;
        }

        .mediaIcons:hover {
            background: rgba(255, 255, 255, 0.05);
        }

        .mediaIcons svg:hover {
            stroke: #FFFFFF;
        }

        .sent {
            background: #1F9494;
            border: none;
            max-width: 45px;
            height: 45px;
            border-radius: 52px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 6px 14px rgba(26, 77, 255, 0.4);
            transition: all 0.2s;
        }

        .sent:hover {
            background: #3f6aff;
            transform: scale(1.02);
            box-shadow: 0 10px 22px #1f4eff;
        }

        .sent svg {
            size: 120px;
            width: 24px;
            height: 24px;
            fill: white;
            stroke: none;
        }

        @media (max-width: 800px) {
            .messenger {
                flex-direction: column;
                height: 100vh;
                border-radius: 28px;
            }
            .sidebar {
                width: 100%;
                max-height: 35%;
                border-right: none;
                border-bottom: 1px solid rgba(255,255,255,0.05);
            }

            .main-chat {
                height: 65%;
            }
            .chats-header {
                padding: 16px 20px;
            }
            .message-message-list {
                width: 50%
                padding: 150px;
            }

            .files-container {
                bottom: 80px;
                right: 20px;
            }

            .chat-list li {
                font-size: 15px;
            }
        }

