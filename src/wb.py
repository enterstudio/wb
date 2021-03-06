#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Name:
  Power_wb, a command-line tool for Weibo.

Version:
  beta, nothing reserved

Author:
  Lane(zhanglintc)

Description:
  Based on "lxyu/weibo", work on Python 2.x.x, support Linux/Mac/Windows.
  Support automatic installation by using "python setup.py".
  More details visit: https://github.com/zhanglintc/wb


                   _ooOoo_ 
                  o8888888o 
                  88" . "88 
                  (| -_- |) 
                  O\  =  /O 
               ____/`---'\____ 
             .'  \\|     |//  `. 
            /  \\|||  :  |||//  \ 
           /  _||||| -:- |||||-  \ 
           |   | \\\  -  /// |   | 
           | \_|  ''\---/''  |   | 
           \  .-\__  `-`  ___/-. / 
         ___`. .'  /--.--\  `. . __ 
      ."" '<  `.___\_<|>_/___.'  >'"". 
     | | :  `- \`.;`\ _ /`;.`/ - ` : | | 
     \  \ `-.   \_ __\ /__ _/   .-` /  / 
======`-.____`-.___\_____/___.-`____.-'====== 
                   `=---=' 
"""

from defs import *
import defs

# disable warnings
import warnings
warnings.filterwarnings("ignore")

##########################################################################
# Functions are defined below
##########################################################################
def set_display_encoding(encoding):
    """
    change dispaly encoding...
    """

    n = int(encoding)

    if n is CONST_WRONG_ENCODE:
        cprint('')
        cprint('Please choose the encoding you want to set:\n')
        cprint('1: utf-8')
        cprint('2: gbk')
        cprint('')
        cprint('Your current encoding is: [/{}, red/]'.format(defs.GLOBAL_ENCODING))
        cprint('')

    elif not CONST_ENCODE_MIN < n < CONST_ENCODE_MAX:
        cprint("")
        cprint('Not valid, please type "wb -e" to see available encoding\n')

    else:
        database_handler('set_encode', data = [n])
        if n is CONST_UTF8:
            cprint('')
            cprint('Encoding has changed to UTF-8\n')

        elif n is CONST_GBK:
            cprint('')
            cprint('Encoding has changed to GBK\n')

def open_weibo_or_target(client, number):
    """
    Try to open a weibo by using default browser.
    If weibo number is given, open this weibo,
    otherwise open "weibo.com" directly.

    API refer to:
    http://open.weibo.com/wiki/2/statuses/querymid

    Specific weibo URL is something like: weibo.com/uid/mid
    We can use API "querymid" to get "mid" and concatenate the target URL
    """

    # not specific
    if number == "NULL":
        isOpen = webbrowser.open_new_tab('http://weibo.com')

    # specific
    else:
        ret = database_handler("query", number = number)
        recv = client.get('statuses/querymid', id = ret.id, type = 1)
        isOpen = webbrowser.open_new_tab("http://weibo.com/{0}/{1}".format(ret.uid, recv.mid))

    if not isOpen:
        cprint("[/Web Browser is not available..., red/]")

def database_handler(handle_type, data = None, number = None):
    """
    Database management function.

    Database design:
      encode:
        | encode |
            utf-8: 1  (default)
            gbk:   2

      weibo:
        | number int | uid int | id int | cid int |

    parameters:
        handle_type:
            insert:     insert data to database
            query:      get data from database
            get_encode: get encode value from database
            set_encode: set encode value to database
            clean:      clean entire table

        data:
            a list of input data.

            data[0]: number  or  encode
            data[1]: uid
            data[2]: id
            data[3]: cid

        number:
            displaying number of weibos, use to get a specific weibo id & cid

    return:
        a JsonDict of output data.

        ret.number: number
        ret.uid:    uid
        ret.id:     id
        ret.cid:    cid
        ret.encode: encode
    """

    ret = JsonDict()

    # prepare for using database
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()

    # create database table
    try:
        c.execute('create table encode(encode int)')
        c.execute('create table weibo(number int, uid int, id int, cid int)')        
    except sqlite3.OperationalError:
        pass # do nothing if table already exists

    # set encode default value
    if not c.execute('select * from encode').fetchone():
        c.execute('insert into encode values (1)') # default utf-8

    # main process
    if handle_type is 'insert':
        # clean table before use
        c.execute("delete from weibo")

        for item in data:
            try:
                c.execute('insert into weibo values (?, ?, ?, ?)', item)

            except sqlite3.OperationalError:
                cprint("DATABASE INSERT ERROR: please remove wb/src/data.db and try again")

        ret = None

    elif handle_type is 'query':
        query = c.execute('select * from weibo where number={0}'.format(number)).fetchone() # may be unsafe, see Python sqlite3 help file
        ret.number = query[0]
        ret.uid    = query[1]
        ret.id     = query[2]
        ret.cid    = query[3]

    elif handle_type is 'get_encode':
        query = c.execute('select * from encode').fetchone()
        ret.encode = query[0]

    elif handle_type is 'set_encode':
        # clean table before use
        c.execute("delete from encode")

        c.execute('insert into encode values (?)', data) # default utf-8

    elif handle_type is 'clean':
        c.execute("delete from weibo")
        ret = None

    else:
        pass

    # finish use database
    conn.commit()
    conn.close()

    # return
    return ret

def log_in_to_weibo():
    """
    Log in to weibo and get the ACCESS_TOKEN.
    If success, store it to 'token' file,
    if not, do nothing.
    """

    cprint('')
    cprint("please enter your username and password below\n")

    client = Client(API_KEY, API_SECRET, REDIRECT_URI)

    USERID = input("username: ")
    USERPASSWD = getpass.getpass("password: ") # getpass() makes password invisible

    cprint('')
    cprint('logging...')
    code = make_access_token(client, USERID, USERPASSWD)
    if not code: # while log in failed
        cprint('') # a blank line to make better look
        cprint("bad username or password, please try again!\n")

    # after got code, store it
    else:
        client.set_code(code)
        fw = open(TOKEN_PATH, 'wb')
        pickle.dump(client.token, fw)
        fw.close()
        cprint('')
        cprint("log in to weibo.com successfully\n")

def log_in_to_weibo_manual():
    """
    Log in to weibo and get the ACCESS_TOKEN.
    This method need user to copy and paste code itself.
    """

    client = Client(API_KEY, API_SECRET, REDIRECT_URI)
    isOpen = webbrowser.open_new_tab(client.authorize_url)
    if not isOpen:
        cprint("[/Web Browser is not available..., red/]")
        return

    os.system('cls') if global_plat == 'Win' else os.system('clear')
    code = input("paste code here: ")

    client.set_code(code)
    fw = open(TOKEN_PATH, 'wb')
    pickle.dump(client.token, fw)
    fw.close()
    cprint('')
    cprint("log in to weibo.com successfully\n")

def log_out_from_weibo():
    """delete login informations"""

    try:
        os.remove(TOKEN_PATH)
        os.remove(DATABASE_PATH)

        cprint("logged out and cleaned files successful")

    except:
        cprint("you've already logged out or file delete error")

def make_access_token(client, USERID, USERPASSWD):
    """
    Refer to: http://www.cnblogs.com/wly923/archive/2013/04/28/3048700.html
    This function can automatically get 'code' from redirected URL and return it.
    """

    params = urllib.urlencode({
        'action':'submit',
        'withOfficalFlag':'0',
        'ticket':'',
        'isLoginSina':'',
        'response_type':'code',
        'regCallback':'',
        'redirect_uri':REDIRECT_URI,
        'client_id':API_KEY,
        'state':'',
        'from':'',
        'userId':USERID,
        'passwd':USERPASSWD,
        })

    login_url = 'https://api.weibo.com/oauth2/authorize'

    url = client.authorize_url
    content = urllib2.urlopen(url)

    if content:
        headers = { 'Referer' : url }
        request = urllib2.Request(login_url, params, headers)
        opener = get_opener(False)
        urllib2.install_opener(opener)

        try:
            f = opener.open(request)
            return_redirect_uri = f.url
        except urllib2.HTTPError, e:
            return_redirect_uri = e.geturl()

        if return_redirect_uri == login_url:
            code = False
        else:
            code = return_redirect_uri.split('=')[1]

    else:
        code = False

    return code

def update_access_token():
    """Try to load ACCESS_TOKEN from 'token' file"""

    try:
        fr = open(TOKEN_PATH, 'rb')
        ACCESS_TOKEN = pickle.load(fr)
        fr.close()

    except IOError:
        ACCESS_TOKEN = None

    return ACCESS_TOKEN

def comments_to_me_To_File(client, start_page, end_page):
    """
    Download comments from 'start_page' to 'end_page'

    API refer to:
    http://open.weibo.com/wiki/2/comments/to_me

    Deprecated, merely use => by zhanglin 2014.11.21
    """

    my_page = start_page

    fw = open('comments.txt', 'wb')

    while my_page <= end_page:
        try:
            cprint('Page {0} is downloading'.format(my_page))
            received = client.get('comments/to_me', count = 20, uid = 1804547715, page = my_page)

        except:
            cprint('Page {0} is downloading has failed'.format(my_page))
            continue

        fw.write('\n\nPage {0}:\n'.format(my_page).encode(defs.GLOBAL_ENCODING))
        for item in received.comments:
            to_be_written = '{0}: {1} by {2}\n'.format(item.created_at, item.text, item.user.name)
            fw.write(to_be_written.encode(defs.GLOBAL_ENCODING))

        fw.flush()
        my_page += 1

    fw.close()
    cprint('All the comments have been downloaded')

def get_comments_to_me(client, count):
    """
    Get comments to me and display in screen.

    API refer to:
    http://open.weibo.com/wiki/2/comments/to_me
    http://open.weibo.com/wiki/2/comments/mentions

    Display example:
    No.1: (to_me)
    11:27:05 | Feb 07 2015 | from @大Date:
    回复@Lane麟:我也不几道了
    =========================================================
    回复@大Date:先解释解释啊
    =========================================================

    """

    if int(count) > 200:
        cprint("error: cannot get comments more than 200\n")
        return

    os.system('cls') if global_plat == 'Win' else os.system('clear')
    cprint('') # a blank line makes better look
    cprint("getting latest {0} comments to me...\n".format(count))

    # get comments to me & add type
    received_to_me = client.get('comments/to_me', count = count)
    for item in received_to_me.comments:
        item['type'] = 'to_me'

    # get comments mentioned me & add type
    received_mentions = client.get('comments/mentions', count = count)
    for item in received_mentions.comments:
        item['type'] = 'mentions'

    to_be_saved = []

    # combine comments to me & comments mention
    comments_all = received_to_me.comments + received_mentions.comments
    # [ lambda x, y: cmp(y, x) ] makes new -> old (descending, bigger -> smaller)
    # [ lambda x, y: cmp(x, y) ] makes old -> new (ascending, smaller -> bigger)
    # here is new -> old
    comments_all = sorted(comments_all, cmp = lambda x, y: cmp(make_time_numeric(y.created_at), make_time_numeric(x.created_at)))

    index = int(count)
    for item in comments_all[int(count) - 1::-1]: # [from:to:-1] makes old -> new
        to_be_saved.append([index, item.status.user.id, item.status.id, item.id]) # cache ids and cids

        # cprint comment to me or mentions to me
        cprint\
            (u'No.{0}: ({1})\n{2} | from @{3}:\n[/{4}, red/]'.format
                (
                    index, # 0
                    item.type, # 1
                    convert_time(item.created_at), # 2
                    item.user.name, # 3
                    item.text, # 4
                )
            )

        # cprint original weibo or comment
        cprint('=========================================================')
        if "reply_comment" in item:
            cprint(item.reply_comment.text)
        else:
            cprint(item.status.text)
        cprint('=========================================================')
        cprint('') # only for better look

        index -= 1

    # save data to database
    database_handler('insert', data = to_be_saved)

def get_friends_timeline(client, count):
    """
    Show friends_timeline in the screen

    API refer to:
    http://open.weibo.com/wiki/2/statuses/friends_timeline

    Display example:
    1. Without retweet:
        No.1:
        11:12:42 | Jan 11 2015 | by @王尼玛:
        王尼玛教你学数学

    2. With retweet:
        No.1:
        12:32:07 | Jan 11 2015 | by @王尼玛:
        看着大家都在@邓超 我也来一发，超哥赶紧来学数学了！
        =========================================================
        11:12:42 | Jan 11 2015 | by @王尼玛:
        王尼玛教你学数学
        =========================================================
    """

    if int(count) > 100:
        cprint("error: cannot get weibos more than 100\n")
        return

    os.system('cls') if global_plat == 'Win' else os.system('clear')
    cprint('') # a blank line makes better look
    cprint("getting latest {0} friend's weibo...\n".format(count))

    received = client.get('statuses/friends_timeline', count = count)
    to_be_saved = []

    index = int(count) # used in No.{index} below
    for item in received.statuses[::-1]: # from old to new
        # ignore AD
        if item.get('ad'):
            continue

        retweet = item.get('retweeted_status') # if this is retweet or not

        to_be_saved.append([index, item.user.id, item.id, None])

        # cprint normal content first
        cprint\
            (u'No.{0}:\n{1} | by @{2}:\n{3}'.format
                (
                    str(index),
                    convert_time(item.created_at),
                    item.user.name,
                    item.text,
                )
            )

        # if this is not retweet, just cprint a blank line
        if not retweet:
            cprint('')

        # if this is retweet, cprint the retweeted content
        else:
            cprint('=========================================================')

            # if original Weibo has been deleted, only cprint text
            if 'deleted' in item.retweeted_status:
                cprint((item.retweeted_status.text))

            # else cprint normally
            else:
                cprint\
                (u'{0} | by @{1}:\n{2}'.format
                    (
                        convert_time(item.retweeted_status.created_at),
                        item.retweeted_status.user.name,
                        item.retweeted_status.text,
                    )
                )

            cprint('=========================================================')
            cprint('')

        index -= 1

    database_handler('insert', data = to_be_saved)

def get_statuses_mentions(client, count):
    """
    Get mentions and display it on the screen.

    API refer to:
    http://open.weibo.com/wiki/2/statuses/mentions(貌似此API新浪对于非授权用户已经不予返回值了... 我晕, 做着玩儿都玩儿不了了)
    http://open.weibo.com/wiki/2/comments/mentions

    Display example:
    1. Without retweet:
        No.1: (mentions)
        23:22:39 | Oct 27 2014 | by @左手心的寂寞在北京:
        有点感动

    2. With retweet:
        No.1: (mentions)
        23:22:39 | Oct 27 2014 | by @左手心的寂寞在北京:
        有点感动
        =========================================================
        19:03:50 | Oct 27 2014 | by @Lane麟:
        #猥亵罪对象加男性# 终于可以安心的出门了。
        =========================================================

    """

    if int(count) > 200:
        cprint("error: cannot get mentions more than 200\n")
        return

    os.system('cls') if global_plat == 'Win' else os.system('clear')
    cprint('') # a blank line makes better look
    cprint("getting latest {0} mentions...\n".format(count))

    # received = client.get('statuses/mentions', count = count)

    # get mentions & add type
    received_mentions = client.get('statuses/mentions', count = count)
    for item in received_mentions.statuses:
        item['type'] = 'mentions'

    # get comments mentioned me & add type
    received_comment_mentions = client.get('comments/mentions', count = count)
    for item in received_comment_mentions.comments:
        item['type'] = 'comment_mentions'

    to_be_saved = []

    # combine mentions & comments mention
    mentions_all = received_mentions.statuses + received_comment_mentions.comments
    # [ lambda x, y: cmp(y, x) ] makes new -> old (descending, bigger -> smaller)
    # [ lambda x, y: cmp(x, y) ] makes old -> new (ascending, smaller -> bigger)
    # here is new -> old
    mentions_all = sorted(mentions_all, cmp = lambda x, y: cmp(make_time_numeric(y.created_at), make_time_numeric(x.created_at)))

    index = int(count)
    for item in mentions_all[int(count) - 1::-1]: # [from:to:-1] makes old -> new
        retweet = item.get('retweeted_status')

        try: # comment_mentions
            to_be_saved.append([index, item.status.user.id, item.status.id, None])

        except AttributeError: # mentions
            to_be_saved.append([index, item.user.id, item.id, None])

        cprint\
            (u'No.{0}: ({1})\n{2} | by @{3}:\n{4}'.format
                (
                    str(index), # 0
                    item.type, # 1
                    convert_time(item.created_at), # 2
                    item.user.name, # 3
                    item.text, # 4
                )
            )

        # without retweet
        if not retweet:
            cprint('')

        # with retweet
        else:
            cprint('=========================================================')
            # if original Weibo has been deleted, only cprint text
            if 'deleted' in item.retweeted_status:
                cprint(item.retweeted_status.text)

            # else cprint normally
            else:
                cprint\
                (u'{0} | by @{1}:\n{2}'.format
                    (
                        convert_time(item.retweeted_status.created_at),
                        item.retweeted_status.user.name,
                        item.retweeted_status.text,
                    )
                )
            cprint('=========================================================')
            cprint('')

        index -= 1

    # save data to database
    database_handler('insert', data = to_be_saved)

def show_status(client):
    """
    Show unread informations.

    API refer to:
    http://open.weibo.com/wiki/2/remind/unread_count
    """

    cprint('') # a blank line makes better look
    cprint("getting status...\n")

    received = client.get('remind/unread_count')

    cprint("unread weibo    => {0}".format(received.status))
    cprint("new comments    => {0}".format(received.cmt))
    cprint("new mentions    => {0}".format(received.mention_status + received.mention_cmt))
    cprint("direct messages => {0}".format(received.dm))
    cprint('') # blank line makes better look

def post_statuses_update(client, text):
    """ 
    Update a new weibo(text only) to Sina

    API refer to:
    http://open.weibo.com/wiki/2/statuses/update
    """

    cprint('')
    cprint('sending...\n')

    try:
        client.post('statuses/update', status = text)
        cprint('=========================================================')
        cprint(text)
        cprint('=========================================================')
        cprint('has been successfully posted!\n')

    except RuntimeError as e:
        cprint("sorry, send failed because: {0}\n".format(str(e)))

def post_statuses_upload(client, text):
    """
    Upload a new weibo(with picture) to Sina
    Currently not in use from 2014.11.12
    Maybe reuse in the future

    API refer to:
    http://open.weibo.com/wiki/2/statuses/upload
    """

    picture = tkFileDialog.askopenfilename() # get picture by GUI

    cprint('')
    cprint('sending...\n')

    try:
        f = open(picture, 'rb')
        resp = client.post('statuses/upload', status = text, pic = f)
        f.close()

        webbrowser.open_new_tab(resp['original_pic'])

        cprint('=========================================================')
        cprint(text + '\n(with picture)')
        cprint('=========================================================')
        cprint('has been successfully posted!\n')

    except (RuntimeError, IOError) as e:
        cprint("sorry, send failed because: {0}\n".format(str(e)))

def post_statuses_repost(client, number, status):
    """
    function:
        Forward(repost) a weibo.

    parameters:
        number: number of weibo you wish to forward
        status: your comment while forward this weibo.

    API refer to:
    http://open.weibo.com/wiki/2/statuses/repost
    """

    cprint("forwarding...")

    ret = database_handler('query', number = int(number))

    client.post('statuses/repost', id = ret.id, status = status)

    cprint("succeed!!!")

def post_comment_reply(client, number, comment):
    """
    function:
        Make a reply. If replying to a weibo, set cid as None.

    parameters:
        number: number of weibo or comment wish to reply
        comment: your comment

    API refer to:
    http://open.weibo.com/wiki/2/comments/create
    http://open.weibo.com/wiki/2/comments/reply
    """

    cprint("replying...")

    ret = database_handler('query', number = int(number))

    # reply to a comment
    if ret.cid:
        client.post('comments/reply', id = ret.id, cid = ret.cid, comment = comment)

    # reply to a weibo
    else:
        client.post('comments/create', id = ret.id, comment = comment)

    cprint("succeed!!!")

def creat_parser():
    parser = argparse.ArgumentParser(
        prog = "wb",
        # usage = 'wb -option [option1, option2...]',
        description = "wb -- A command-line tool for Weibo",
        epilog = 'This code is out sourced on Github,\
                    please visit https://github.com/zhanglintc/wb\
                    for further infomations',
        prefix_chars = '-', # remove '/' to solve image sending problem(there is '/' in path)
        fromfile_prefix_chars = '@',
        argument_default = argparse.SUPPRESS,
        )

    parser.add_argument('-authorize', metavar = '-a', nargs = '?', const = 'True', help = "sign in to 'weibo.com', wb -a m for manual sign in")
    parser.add_argument('-comment', metavar = '-c', nargs = '?', const = 5, help = "get comments to me")
    parser.add_argument('-delete', metavar = '-d', nargs = '?', const = 'True', help = "coming soon")
    parser.add_argument('-encode', metavar = '-e', nargs = '?', const = CONST_WRONG_ENCODE, help = "set display encoding")
    parser.add_argument('-forward', metavar = '', nargs = 2, help = "forward a weibo")
    parser.add_argument('-get', metavar = '-g', nargs = '?', const = 5, help = "get latest N friend's timeline")
    parser.add_argument('-image', metavar = '-i', nargs = '?', const = 'share image', help = "post a new weibo with image")
    parser.add_argument('-mention', metavar = '-m', nargs = '?', const = 5, help = "get latest N mentions")
    parser.add_argument('-open', metavar = '-o', nargs = '?', const = 'NULL', help = "open weibo.com or a target")
    parser.add_argument('-post', metavar = '-p', nargs = 1, help = "post a new weibo")
    parser.add_argument('-quit', metavar = '-q', nargs = '?', const = 'True', help = "delete token and quit")
    parser.add_argument('-reply', metavar = '', nargs = 2, help = "reply a weibo")
    parser.add_argument('-tweet', metavar = '-t', nargs = 1, help = "post a new weibo(alias of -p)")
    parser.add_argument('common', nargs = '?', help = "status/...")

    return parser

def wb_command():
    parser = creat_parser()
    params = vars(parser.parse_args())
    # cprint(params) ## debug use only

    # default entry here
    if not params:
        try:
            show_status(client)
        except:
            cprint('failed, please type "wb -a" to log in.')
            cprint('')
            cprint('')
            cprint('- Note: type "wb -h/--help" to see usages.\n')

    # Common command -S
    # available commands:
    # 1. wb status => get current status
    elif params.get('common') == 'status':
        show_status(client)
    # Common command -E

    # Hyphen command -S
    elif params.get('authorize'):
        if params.get('authorize') == 'm':
            log_in_to_weibo_manual()
        else:
            log_in_to_weibo()

    elif params.get('encode'):
        set_display_encoding(params['encode'])

    elif params.get('delete'):
        # log_out_from_weibo()
        cprint("delete coming soon")

    elif params.get('forward'):
        post_statuses_repost(client, params['forward'][0], params['forward'][1])

    elif params.get('get'):
        get_friends_timeline(client, params['get'])

    elif params.get('image'):
        if is_TKinter_exist:
            post_statuses_upload(client, params['image'])
        else:
            cprint("[/Send with image is not supported!!!, red/]")

    elif params.get('mention'):
        get_statuses_mentions(client, params['mention'])

    elif params.get('open'):
        open_weibo_or_target(client, params.get('open'))

    elif params.get('reply'):
        post_comment_reply(client, params['reply'][0], params['reply'][1])

    elif params.get('post'):
        post_statuses_update(client, params['post'][0])

    elif params.get('quit'):
        log_out_from_weibo()

    elif params.get('tweet'):
        post_statuses_update(client, params['tweet'][0])

    elif params.get('comment'):
        get_comments_to_me(client, params['comment'])
    # Hyphen command -E

    else:
        cprint('')
        cprint('- Note: unrecognized command, type "wb -h/--help" to see usages.\n')

if __name__ == "__main__":
    ACCESS_TOKEN = update_access_token()
    client = Client(API_KEY, API_SECRET, REDIRECT_URI, ACCESS_TOKEN)

    # get encoding
    query = database_handler('get_encode').encode
    if query == CONST_UTF8:
        defs.GLOBAL_ENCODING = "utf-8"
    elif query == CONST_GBK:
        defs.GLOBAL_ENCODING = "gbk"

    # do call the parameters process function
    wb_command()





