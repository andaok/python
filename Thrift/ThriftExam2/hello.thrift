service hello 
{
   string GetSysVer()
   
   string FileTransfer(1:string filename,2:binary content)
   
   bool FileExists(1:string filename)
}
