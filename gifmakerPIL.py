import struct
from pathlib import Path
from PIL import Image
import numpy as np

from tqdm import tqdm

# 透明贴图路径，形如.../character/marisa/sit000.png
IMAGES_PATH = Path(r"./source/character")
# 动作xml路径，形如.../character/marisa/marisa.xml
XMLS_PATH = Path(r"./source/character")
# 非透明贴图路径，形如.../character/marisa/sit000.png
NOALPHA_PATH = Path(r"./noalpha/character")
# 生成的gif保存路径，形如.../character/marisa/505.gif
SAVE_PATH = Path(r"./gifs/character")

# 一个角色的所有动作
class character:
    
    """
    xml典型结构：
    <move id="112" index="0" loop="0" movelock="0" actionlock="0">
		<frame image="down000.bmp" index="0" unknown="0" xtexoffset="0" ytexoffset="0" texwidth="128" texheight="128" xoffset="117" yoffset="217" duration="3" rendergroup="0">
			<traits damage="0" proration="0" chipdamage="0" spiritdamage="0" untech="0" power="0" limit="0" onhitplayerstun="0" onhitenemystun="0" onblockplayerstun="0" onblockenemystun="0" onhitcardgain="0" onblockcardgain="0" onairhitsetsequence="0" ongroundhitsetsequence="0" xspeed="0" yspeed="0" onhitsfx="0" onhiteffect="0" attacklevel="0">
				<down/>
				<grabinvul/>
				<melleinvul/>
				<bulletinvul/>
				<fflag21FLIP_VELOCITY/>
			</traits>
			<effect xpivot="0" ypivot="0" xpositionextra="0" ypositionextra="0" xposition="0" yposition="0" unknown02="0" xspeed="0" yspeed="0"/>
		</frame>
		<frame image="down001.bmp" index="1" unknown="0" xtexoffset="0" ytexoffset="0" texwidth="63" texheight="61" xoffset="77" yoffset="113" duration="3" rendergroup="0">
			<traits damage="0" proration="0" chipdamage="0" spiritdamage="0" untech="0" power="0" limit="0" onhitplayerstun="0" onhitenemystun="0" onblockplayerstun="0" onblockenemystun="0" onhitcardgain="0" onblockcardgain="0" onairhitsetsequence="0" ongroundhitsetsequence="0" xspeed="0" yspeed="0" onhitsfx="0" onhiteffect="0" attacklevel="0">
				<down/>
				<grabinvul/>
				<melleinvul/>
				<bulletinvul/>
				<fflag21FLIP_VELOCITY/>
			</traits>
			<effect xpivot="0" ypivot="0" xpositionextra="0" ypositionextra="0" xposition="0" yposition="0" unknown02="0" xspeed="0" yspeed="0"/>
		</frame>
	</move>
    """
    # 读取xml文件，获取角色所有动作，但是每一个movId为{id}_{index}_{loop}，生成时gif生成每个movId
    def readPos(self):
        print(self.charac)
        import xml.etree.ElementTree as ET
        movList = {}

        # 解析XML文件
        tree = ET.parse(self.xmlPath)

        # 获取根元素
        root = tree.getroot()

        # 遍历所有的'frame'元素
        for move in root.iter('move'):
            movId = '_'.join((move.attrib['id'], move.attrib['index'], move.attrib['loop']))
            
            theMov = []
            # 打印出'frame'元素的所有属性
            for frame in move.iter('frame'):
                theMov.append(frame.attrib)
                theMov[-1]['image'] = self.imagePath / (frame.attrib['image'].replace('.bmp', '.png'))

            movList[movId] = theMov
            
        self.movList = movList
        
    # 读取xml文件，获取角色所有动作，但是每一个movId为{id}，根据index顺序和loop次数生成
    def readPos_loop(self):
        import xml.etree.ElementTree as ET
        movList = {}

        # 解析XML文件
        tree = ET.parse(self.xmlPath)

        # 获取根元素
        root = tree.getroot()

        # 遍历所有的'frame'元素
        for move in root.iter('move'):
            
            movId = move.attrib['id']
            if movId not in movList:
                movList[movId] = []
            
            for _ in range(int(move.attrib['loop'])+1):
                theMov = []
                # 打印出'frame'元素的所有属性
                for frame in move.iter('frame'):
                    theMov.append(frame.attrib.copy())
                    theMov[-1]['image'] = self.imagePath / (frame.attrib['image'][:].replace('.bmp', '.png'))
                movList[movId].extend(theMov)
            
        self.movList = movList
            

    """
    结构：
    self.movList = 
    {
        '504': [
            {'image': Path(...), 'xoffset': '0', 'yoffset': '0', ...},
            ],
        
        ...
    }
    """
    def __init__(self, charac):
        self.imagePath = IMAGES_PATH / charac
        self.xmlPath = XMLS_PATH / charac / (charac + '.xml')
        self.savePath = SAVE_PATH / charac
        if not self.savePath.exists():
            self.savePath.mkdir(parents=True)
        self.charac = charac
        
        self.readPos_loop()
        
    # transparentize, then move the file in noalphapath to imagepath
    # 透明化，然后将noalphapath中的文件移动到imagepath，
    def alpha_move(self, destImage: Path):
        tgtImage = destImage.relative_to(IMAGES_PATH)
        tgtImage = NOALPHA_PATH / tgtImage
        
        bgColor = (0, 123, 140) #非透明图的背景色
        
        try:
            image = Image.open(tgtImage)
        except FileNotFoundError as e:
            print('File not found in NOALPHA_PATH:', tgtImage)
            return
        
        # If the image does not have an alpha (transparency) channel, add one
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        # Get the data of the image
        data = image.getdata()

        # Create a new list to hold the new image data
        new_data = []

        # Iterate over each pixel in the data
        for item in data:
            # If the pixel is the same color as bgColor, make it fully transparent
            if item[0] == bgColor[0] and item[1] == bgColor[1] and item[2] == bgColor[2]:
                new_data.append((item[0], item[1], item[2], 0))
            else:
                new_data.append(item)

        # Update the image data
        image.putdata(new_data)

        # Save the image
        image.save(destImage)
        
    # 生成gif
    # timePerDura: 每一个duration持续的时间（毫秒）
    def generate(self, movId, timePerDura=1000/60):
        # timePerDura = int(timePerDura) # 帧率
        movFrames = self.movList[movId]
        backgrounds = []
        durations = []
        for frame in movFrames:
            image_file = frame['image']
            try:
                image = Image.open(image_file)
            except FileNotFoundError as e:
                self.alpha_move(image_file)
                image = Image.open(image_file)

            background = Image.new('RGBA', (800, 600)) # 大画布
                
            xoffset = 400-int(frame.get('xoffset'))
            yoffset = 300-int(frame.get('yoffset'))
            durations.append(timePerDura * int(frame.get('duration')))

            # 将图像粘贴到背景图像的指定位置
            image = image.resize((image.width * 2, image.height * 2))
            background.paste(image, (xoffset, yoffset))
            
            backgrounds.append(background)

        
        # 剪切多余像素
        def crop_to_max_pixel(backgrounds):
            # Initialize the min and max coordinates
            min_x, min_y, max_x, max_y = float('inf'), float('inf'), 0, 0

            # Iterate over each image
            for background in backgrounds:
                # Convert the image to a NumPy array
                np_image = np.array(background)

                # Find the non-zero elements (i.e., the pixels of the character)
                non_zero_pixels = np.nonzero(np_image)

                # Update the min and max coordinates
                min_x = min(min_x, np.min(non_zero_pixels[1]))
                min_y = min(min_y, np.min(non_zero_pixels[0]))
                max_x = max(max_x, np.max(non_zero_pixels[1]))
                max_y = max(max_y, np.max(non_zero_pixels[0]))

            # Crop each image to the max pixel size
            cropped_backgrounds = [background.crop((min_x, min_y, max_x, max_y)) for background in backgrounds]

            return cropped_backgrounds

        try:
            backgrounds = crop_to_max_pixel(backgrounds)
        except Exception as e:
            print('crop:', e, end=': ')
            print(self.charac, movId)
        
        # Change black (also shades of blacks) pixels to almost black
        # 否则生成的gif在部分图片查看器中，纯黑色像素被识别为透明像素
        for background in backgrounds:
            datas = background.getdata()

            newData = []
            for item in datas:
                # change all black (also shades of blacks) pixels to almost black
                if item[0] < 1 and item[1] < 1 and item[2] < 1:
                    newData.append((1, item[1], item[2], item[3]))
                else:
                    newData.append(item)
            background.putdata(newData)
            
        # 确保每一帧的持续时间都在0到65535的范围内
        # 否则生成时gif报错
        durations = [min(max(duration, 0), 65535) for duration in durations]
        if any(x == 65535 for x in durations):
            print(movId, 'frame too long')
        if all(x == 65535 for x in durations):
            print(movId, 'all too long')
            durations = [1000 for _ in durations]
        
        try:
            # 生成的gif是透明背景的
            backgrounds[0].save(self.savePath / f'{movId}.gif', save_all=True, append_images=backgrounds[1:], loop=0, disposal=2, duration=durations)
        except struct.error:
            print('struct.error for:', self.charac, movId, )
            print(durations)
            return
        except Exception as e:
            raise
        
        if not (self.savePath / f'{movId}.gif').exists():
            print('Creation failed for:', self.charac, movId)
        
    # 生成一个角色的所有gif
    # skip: 是否跳过已存在的gif
    def generate_all(self, skip=False, progress='1/1'):
        if self.allExist():
            print(self.charac, 'all exist')
            return
        for movId in tqdm(self.movList, desc=' '.join((progress, self.charac))):
            if skip:
                if (self.savePath / f'{movId}.gif').exists():
                    continue
            self.generate(movId)
            
    # 所有gif文件是否存在
    def allExist(self):
        for movId in self.movList:
            if not (self.savePath / f'{movId}.gif').exists():
                print(self.charac, movId, 'not exist')
                return False
        return True
    
    # 目录下是否有多余的gif文件
    def numberMatch(self):
        return len(list(self.savePath.glob('*.gif'))) == len(self.movList)

# 所有角色
class allCharacters:
    
    def __init__(self) -> None:
        self.charac_names = [i.name for i in IMAGES_PATH.iterdir() if i.name not in ['common', 'ui'] and i.is_dir()]
        self.characsObj = [character(i) for i in self.charac_names]
        
    # 生成所有角色的所有gif
    def generateAll(self, skip=True):
        for charac in self.characsObj:
            
            charac.generate_all(skip=skip, progress=f'{self.characsObj.index(charac)+1}/{len(self.characsObj)}')
            
        print('All charac all files exist?', self.allExist())
        
        print('All charac file number match?', self.numberMatch())
            
    def allExist(self):
        for charac in self.characsObj:
            if not charac.allExist():
                return False
        return True
    
    def numberMatch(self):
        for charac in self.characsObj:
            if not charac.numberMatch():
                print(charac.charac, 'number not match')
                return False
        return True
                

if __name__ == "__main__":
    # # 生成marisa的504动作
    # character('marisa').generate('504')
    
    # # 生成marisa的所有动作
    # character('marisa').generate_all()
    
    # 生成所有角色的所有动作
    allCharacters().generateAll()
