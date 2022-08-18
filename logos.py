SPLASH = '''
⣿⣿⣛⠛⠛⠛⠛⠛⠛⠛⠿⢶⣦⣄⡀⠀⠀⠀  ________  ________  ________  ________  ________  _______      
⣿⠈⠙⢷⣄⠀⠀⠀⣀⣀⣀⠀⠈⠙⠻⣦⣄⠀ |\\   ____\\|\\   __  \\|\\   __  \\|\\   __  \\|\\   ____\\|\\  ___ \\     
⣿⡀⠀⠀⢙⣷⡾⢿⣛⠻⠻⣷⣄⡀⠀⠘⢿⡄ \\ \\  \\___|\\ \\  \\|\\  \\ \\  \\|\\  \\ \\  \\|\\  \\ \\  \\___|\\ \\   __/|    
⣿⡇⠀⠀⣸⡿⠀⠀⠀⠀⠀⢨⢹⣷⠀⠀⢸⣿  \\ \\_____  \\ \\  \\\\\\  \\ \\   __  \\ \\   _  _\\ \\  \\    \\ \\  \\_|/__  
⣿⡇⠀⠀⢿⣧⡢⣀⠀⠀⠀⡌⣼⡏⠀⠀⢸⣿   \\|____|\\  \\ \\  \\\\\\  \\ \\  \\ \\  \\ \\  \\\\  \\\\ \\  \\____\\ \\  \\_|\\ \\ 
⠘⣷⡄⠀⠀⠙⢿⣮⣥⣤⣶⠾⢿⣅⠀⠀⠈⣿     ____\\_\\  \\ \\_______\\ \\__\\ \\__\\ \\__\\\\ _\\\\ \\_______\\ \\_______\\
⠀⠘⠻⣦⣄⡀⠀⠉⠉⠉⠀⠀⠀⠙⠷⣦⡀⣿    |\\_________\\|_______|\\|__|\\|__|\\|__|\\|__|\\|_______|\\|_______|
⠀⠀⠀⠈⠙⠻⠷⢶⣦⣤⣤⣤⣤⣤⣤⣬⣿⣿    \\|_________|                                                 
 '''

TEXT = ''' ________  ________  ________  ________  ________  _______      
|\\   ____\\|\\   __  \\|\\   __  \\|\\   __  \\|\\   ____\\|\\  ___ \\     
\\ \\  \\___|\\ \\  \\|\\  \\ \\  \\|\\  \\ \\  \\|\\  \\ \\  \\___|\\ \\   __/|    
 \\ \\_____  \\ \\  \\\\\\  \\ \\   __  \\ \\   _  _\\ \\  \\    \\ \\  \\_|/__  
  \\|____|\\  \\ \\  \\\\\\  \\ \\  \\ \\  \\ \\  \\\\  \\\\ \\  \\____\\ \\  \\_|\\ \\ 
    ____\\_\\  \\ \\_______\\ \\__\\ \\__\\ \\__\\\\ _\\\\ \\_______\\ \\_______\\
   |\\_________\\|_______|\\|__|\\|__|\\|__|\\|__|\\|_______|\\|_______|
   \\|_________|                                                 '''

LOGO = '''⣿⣿⣛⠛⠛⠛⠛⠛⠛⠛⠿⢶⣦⣄⡀⠀⠀⠀
⣿⠈⠙⢷⣄⠀⠀⠀⣀⣀⣀⠀⠈⠙⠻⣦⣄⠀
⣿⡀⠀⠀⢙⣷⡾⢿⣛⠻⠻⣷⣄⡀⠀⠘⢿⡄
⣿⡇⠀⠀⣸⡿⠀⠀⠀⠀⠀⢨⢹⣷⠀⠀⢸⣿
⣿⡇⠀⠀⢿⣧⡢⣀⠀⠀⠀⡌⣼⡏⠀⠀⢸⣿
⠘⣷⡄⠀⠀⠙⢿⣮⣥⣤⣶⠾⢿⣅⠀⠀⠈⣿
⠀⠘⠻⣦⣄⡀⠀⠉⠉⠉⠀⠀⠀⠙⠷⣦⡀⣿
⠀⠀⠀⠈⠙⠻⠷⢶⣦⣤⣤⣤⣤⣤⣤⣬⣿⣿'''

HELP = '''Motor Commands:
    on - Turn the motor on
    off - Turn the motor off
    fwd - Step in the forward direction
    bkwd - Step in the reverse directiion
    [A NUMBER] - the number of steps per second, 1 revolution is 1600 steps
    speed [A NUMBER] - set the maximum speed for a motor
    linear - put motor into linear mode
Linear Commands:
    zero - Set zero point for linear motor
    max - Set maximum point for linear motor
    accel [A NUMBER] - Set the acceleration (I RECOMEND 10000)
    step [A NUMBER] - Step motor that far, negative is backwards
    go - toggle back and forth movement
Other Commands:
    exit - Exit the program
    help - display this help screen
Notes:
    Command format: [motor symbol] [commmand] [argument]
    '''

BOLBI = '''⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠀⠈⠀⡀⠄⠠⠐⠀⡂⠄⠄⡐⡀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠄⠈⢀⠀⠄⠂⡀⠁⠄⠂⡐⢀⠂⡂⠅⠤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠂⠀⠐⠀⠐⠀⠈⡀⠠⠐⢀⠐⡈⠄⡁⡂⡂⡂⡂⢅⠑⢔⠀⡀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⡀⠀⡀⠂⠀⠀⠀⠀⠄⠐⠀⢁⠀⠂⠁⠂⠂⠂⡑⠐⢐⠐⢐⠨⠠⠡⢑⠀⠄⢐⠡⠠⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠠⡐⡐⢐⠀⠂⠀⠀⠀⠀⠀⠀⠄⢀⢀⢂⢔⠰⡨⡢⡣⡣⡧⡲⡼⣔⣖⡴⣴⣰⣰⢵⡡⡂⡐⠨⡐⡘⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⡃⠢⠀⠠⠀⢁⠀⠂⠀⠂⠈⢀⠔⡐⢌⠢⠪⡘⢌⠎⡎⡈⠌⡊⢝⠪⡺⣽⣺⣞⡾⡽⡽⣔⠨⢈⢂⠢⠡⢡⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠢⠩⠀⠂⠀⠀⢀⠠⠐⢄⠕⡐⢅⠪⠠⠁⠅⢌⠢⡑⠕⡕⣕⢖⢤⢅⢌⡾⣺⢾⡽⡯⣟⡮⣗⡄⠂⠡⢑⠐⡂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠀⠂⠀⢄⢂⢂⠪⠨⠢⡱⡘⢔⢅⠕⡜⡝⠕⠉⠉⡝⣾⣼⣼⢱⢝⢵⡫⣟⣽⢽⢯⡷⣯⡳⡽⣄⠁⠂⠌⠌⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⡨⠨⢂⠢⠑⢌⠪⡑⢔⢱⢑⢕⢕⢜⢌⢢⢀⢈⢅⣟⣿⣿⣟⣎⡘⡎⣗⢽⢽⠽⣝⢮⢇⠕⢵⢅⠈⠄⡁⡂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠨⡱⠨⡈⡂⠌⠌⡂⢅⢊⢢⢱⢱⣣⡳⣕⢗⢵⢕⡗⣮⡻⡽⣯⣟⢷⡁⢎⡮⡳⢍⣗⢵⢳⡣⡣⢁⢳⡂⠠⠀⡂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠨⡊⡂⡂⢂⠁⡂⢂⠢⢑⢌⢪⢪⡲⣝⢮⢯⣳⢽⡺⣵⡫⣯⢺⣪⡳⣬⣳⢵⢵⡵⡶⠵⣵⣝⡝⡖⣜⢎⠀⢂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠰⢐⠈⠄⠂⠐⢐⠨⢐⢐⢅⢕⢪⢪⢓⢝⢪⢏⢟⣮⣻⣪⢗⡧⡯⣗⢷⣝⢽⡁⠂⠡⡎⣿⣷⣧⢓⢝⠀⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡑⡐⠈⠄⠨⠐⠠⠨⢐⠰⡐⢅⢣⠱⡑⣌⢂⠂⠑⢕⢗⣗⢽⢊⢫⢪⢗⡽⣵⡻⣜⡤⡬⣿⢷⣻⠅⡂⠐⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢐⠄⠡⢈⠀⠂⠄⢁⠂⠅⡪⠨⡊⡪⡪⣪⡲⣄⠈⡐⢕⢽⢕⢀⠪⠸⡹⢝⢞⣞⣗⣝⢮⡹⢝⢮⠁⠀⠆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠢⡈⠐⡀⠄⢁⠐⠠⠈⡂⢌⠪⡨⠪⡸⡸⡺⡪⡧⣄⠐⠕⢯⢦⡢⡀⡈⡸⣜⣗⢷⢽⢵⣫⢧⣳⢅⢦⡢⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⡂⠕⡀⠅⢀⠂⠠⠐⠀⠡⠐⡠⢑⠌⡪⢐⠱⡩⢝⡺⣪⢏⢆⡁⠳⢹⢪⠮⡫⡺⢸⠹⡹⢽⡺⣽⣺⢽⡕⡝⡮⣟⣶⣀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⡐⠄⠅⡂⠌⡀⠐⠀⠂⢁⠀⠅⢐⠠⢑⢈⠢⢑⠌⡪⢪⢪⢏⣗⢴⣑⢆⢦⡢⡤⣰⢠⡠⡠⡑⢝⢮⢺⢵⣳⠱⡕⣗⢗⡿⡄⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⡀⠌⢌⠐⠄⡁⠄⢈⠀⡁⠠⠀⠂⠐⡈⡐⠠⢑⠠⠑⢌⠪⡪⡪⡪⡳⡕⡯⡳⡹⡪⡮⡳⡕⡇⡎⡎⡪⡪⡣⡳⡑⡕⣗⢽⢽⣻⣂⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢀⠐⡀⠨⢐⠨⠐⠠⠈⠀⠄⠠⠐⠀⡈⠠⠀⢂⢁⠢⠨⠨⡂⠕⢌⢪⠸⡘⡜⢜⢜⠱⡩⢪⠪⡪⡊⢎⠜⢌⢆⠣⢊⠰⡱⡱⣝⢽⢽⡽⡄⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠄⠀⠄⠀⠄⠀⠂⠄⠡⠈⠄⠡⠐⠀⠂⠁⡀⠄⠈⡀⠄⠂⠡⠡⢈⠪⠨⠢⡑⢅⢊⢂⠆⡑⢌⠢⡑⢌⢌⠢⡑⠅⡂⡂⠐⠨⡘⢜⢜⢭⡳⡯⡷⡄⠀⠀⠀⠀
⠀⠀⠀⠀⢄⠀⠀⠀⠐⠀⠀⠅⡁⡁⡁⠅⠨⠀⠅⠂⠀⠄⠂⠀⠠⠈⠀⡁⠂⠡⢑⠑⡈⡂⡂⠢⢁⠊⢄⠑⠨⠐⢀⠡⢐⢌⢪⠀⠨⢐⠨⡊⢎⢮⢺⢽⢽⣳⠄⠀⠀⠀
⠀⠀⡢⠡⠁⢂⠀⠈⠀⠈⠀⠀⠂⠄⠐⡀⠅⠄⠀⠀⠀⠀⠀⠈⠀⠀⡀⠀⠈⠀⠂⠈⠄⠂⠠⠁⠂⠈⠀⠐⢀⢢⠡⡣⡑⢔⢅⢃⠈⡐⡐⠌⡪⢪⡪⣳⣫⢯⣇⠀⠀⠀
⠀⡐⡐⠠⢁⠐⡀⠠⠀⠁⠠⠀⠐⠈⠄⠄⠈⡑⢄⠀⠀⠀⠄⠂⠀⠁⠀⠀⢀⠀⠀⠀⠀⠀⡀⢀⠀⡐⡠⢨⠢⡡⡱⠰⡘⢔⠢⡡⠀⠂⢌⠢⡑⢕⢕⢵⢽⢽⣺⡀⠀⠀
⢐⠀⡂⠡⠐⡀⠄⠀⠀⡈⠀⡀⠄⠀⠀⠀⠁⠠⠈⠝⣄⠀⠀⠀⠀⠀⠄⠀⠄⠠⠀⠄⠡⠨⢈⢂⢂⠆⡪⡐⡑⢌⢂⠣⡊⡢⡑⠄⢀⠁⢂⢂⢊⢪⢪⡣⢯⣳⣳⣳⠀⠀
⠐⡀⠂⠌⠠⠀⠂⠁⠀⡀⠄⠀⢀⠀⠄⠀⠄⠀⠀⠀⠐⢕⢄⠀⠠⠐⠈⠄⢁⠂⠐⢀⠀⢄⢐⢐⠔⡡⢂⠢⡑⠌⠢⡑⢌⠢⡊⠀⠄⠐⢀⢂⢊⢢⠣⡝⡜⡮⡺⣺⠄⠀
⠀⢂⠡⠈⡀⢁⢅⠀⡁⠀⡀⠄⠀⡀⠠⠀⢀⠠⠐⠀⠀⠀⠊⡣⡡⠀⢁⠐⠀⠄⠡⠂⢅⢂⢂⠢⠡⠨⢂⠅⡢⠑⢅⢊⠄⠕⡀⠂⠀⠐⢀⠂⡂⢅⠇⡇⡗⡝⡮⣳⢵⠀
⢕⢄⠐⠠⢀⠢⡂⠂⡀⠂⠀⠀⠄⠀⡀⠄⠠⠀⠄⡠⡈⡆⢕⣀⠑⢕⢢⢊⠢⡱⣈⠨⠐⠐⠄⡑⠨⠨⢐⠨⢐⠡⠡⢂⠊⠔⠀⠀⠈⠀⠄⠐⠠⡡⡃⡇⡇⡏⡮⡳⣝⡀
⠕⠕⡍⡣⡣⡣⡣⡣⡣⡪⡪⡔⡤⢅⠤⡐⠠⡡⢊⠆⢕⠨⢂⠑⠡⠀⠑⢕⠌⠌⡆⡇⠌⠄⠅⠂⠅⡑⢐⠨⢐⠨⠨⠠⠁⠂⠀⢀⢁⢐⢌⢪⢑⢆⢪⢂⢃⠃⡋⠚⡎⡆
⠈⡂⡂⠪⠐⠌⠢⡑⠅⢕⢑⠜⠨⡐⠄⢜⠨⢂⠅⡊⠔⡨⠠⠁⠣⢑⢅⠢⡩⡒⡌⠌⢇⠎⠠⠁⡂⠂⡂⠌⠠⠈⠄⠡⠁⢀⢐⠰⢰⠡⠑⠠⢁⢊⢂⢇⢲⠸⣐⡑⢔⠈
⠀⠄⢀⠡⠀⡁⠡⠀⠅⠂⠂⠁⡁⠀⠅⠅⠊⠄⡁⡂⡑⠜⡌⡢⠀⠠⠀⠑⠨⢊⢪⢢⠡⡈⠠⠁⠠⠁⠄⡈⠄⠁⠅⠢⢐⢐⢐⠡⠁⡈⠄⡁⡂⡐⠐⠠⠡⡑⡱⢸⠨⠂
⠀⠀⠀⠀⠄⠀⠂⠁⠠⠁⡈⠠⠀⠀⠂⡁⠌⠠⠀⠄⠠⠑⠈⡊⠪⠢⡐⡀⡈⠀⠂⠂⡑⠜⡀⠌⠠⠑⠡⠢⢑⠑⡁⠁⠄⠠⠀⠄⡀⢂⠂⡂⠐⢀⠐⡀⠅⢂⢊⠢⡑⠁
'''