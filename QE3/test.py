import win32console
import multiprocessing

def subprocess(queue):
    win32console.FreeConsole() #Frees subprocess from using main console
    win32console.AllocConsole() #Creates new console and all input and output of subprocess goes to this new console
    while True:
        print(queue.get())
        #prints any output produced by main script passed to subprocess using queue

if __name__ == "__main__": 
    queue = multiprocessing.Queue()
    multiprocessing.Process(target=subprocess, args=[queue]).start()
    while True:
        print("Hello World in main console")
        queue.put("Hello work in sub process console")
        #sends above string to subprocess and it prints it into its console

        #and whatever else you want to do in ur main process
