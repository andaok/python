struct User {
    1:string firstname
    2:string lastname
}

exception UserException {
     1:i32 error_code
     2:string error_msg
}

service UserManager{
      string ping(),
      string get_user(1:string firstname,2:string lastname) throws(1:UserException e),
      oneway void clear_list()
}
