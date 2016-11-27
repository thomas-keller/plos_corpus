import xmltodict
import glob
import os

files=glob.glob('./torrent/*.xml')
i=1
for file in files:
    i+=1
    #subprocess.run('tail -n +3 {} > {}'.format(file,file),shell=True)
    f=open(file)
    dat=f.readlines()
    if dat and dat[0][:5]=='<?xml':
        #print('saved!')
        continue
    elif not dat:
        print('garbo file')
        os.remove(file)
    else:
        f=open(file,'w')
        for line in dat[2:len(dat)]:
            f.write(line)
        f.close()
        if i%100==0:
            print(i,len(files))
    #print('it worked')