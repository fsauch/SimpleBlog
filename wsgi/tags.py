def parse_tags(tags):
    # Parse the tags to return a list of tags
    if tags:
        return tags.split(",")
    else:
        return []

def format_tags(taglist):
    # Format the tags for user readability
    return ",".join(taglist)

def inc_tag(tag,db):
    # Increases the count for a given tag
    db.tags.update({"name":tag},{"$inc": {"count":1}}, upsert=True)

def dec_tag(tag,db):
    # Decreases the count for a given tag
    db.tags.update({"name":tag},{"$inc": {"count":-1}}, upsert=True)

def inc_tags(tags, db):
    # Increases the count for a list of tags
    for tag in tags.split(","):
        inc_tag(tag, db)

def dec_tags(article, db):
    # Decreases the count for a list of tags
    tags = article["tags"]
    for tag in tags:
        dec_tag(tag,db)

def diff_tags(tags_o, tags_n):
    # Compute the difference between two sets of tags
    # Returns a map with added and deleted tags
    res={"del":[], "add":[]}
    for tag in tags_o:
        if tag not in tags_n:
            res["del"].append(tag)
    for tag in tags_n:
        if tag not in tags_o:
            res["add"].append(tag)
    return res

def update_tags(tags_o, tags_n, db):
    # Given the list of old and new tags update the counts in DB
    change = diff_tags(tags_o, tags_n)
    for tag in change["add"]:
        inc_tag(tag, db)
    for tag in change["del"]:
        dec_tag(tag, db)

