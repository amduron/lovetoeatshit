author:amduron

使用python实现《吃屎蛇》的原型，无聊的之作。
依赖库PIL模块，pyA20模块，
在pyA20模块中int spi_write等几函数最后一个参数为uint8, 请修改为unsigned int，并重新编译并安装此模块，否则无法正常调用spi接口。
运行前确认：/dev/spidev已经存在 
OS:armlinux
硬件：orange pi, oled 0.96'' spi接口。
硬件联接 
RST- PORT.PC7
D/C - PORT.PC3
d0 -  sck
d1 -  mosi

