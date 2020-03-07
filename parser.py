import json
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor


grammar = Grammar(
    """
    dockerfile            = (comment / from_command /user_command/ ws)*
    from_command          = from spaces (platform)? registry? image_name (image_tag / digest)? (local_name)? ws
    user_command          = user spaces (user_name / user_id) ws
    comment               = comment_start sentence* ws
    
    from                  = spaces* "FROM"
    platform              = "--platform=" word_symbols spaces
    registry              = host (":" port)? "/"
    host                  = (protocol)? ~"[a-zA-Z0-9.-]+"
    protocol              = ("https://" / "http://")
    port                  = ~"[0-9]{1,5}"
    image_name            = ~"[a-zA-Z0-9][a-zA-Z0-9_.-]+"
    image_tag             = ":" ~"[\w][\w.-]{0,127}"
    digest                = "@" algorithm ":" hash
    algorithm             = ~"[a-zA-Z0-9]+"
    hash                  = ~"[a-z0-9]{32,}"
    local_name            = spaces "AS" spaces word_symbols
    
    user                  = spaces* "USER"
    user_name             = unix_user (":" unix_user)?
    unix_user             = ~"[a-z_][a-z0-9_-]*[$]?"
    user_id               = unix_uid (":" unix_uid)?
    unix_uid              = ~"[0-9]{1,5}"
    
    sentence              = spaces* word_symbols (spaces word_symbols)*
    comment_start         = spaces* hashtag spaces*
    hashtag               = "#"
    spaces                = space+
    space                 = " "
    word_symbols          = ~"[\S]+"
    ws                    = ~"\s*"
    """
)


class IniVisitor(NodeVisitor):
    def visit_dockerfile(self, node, visited_children):
        """ Returns the overall output. """
        result = {'comments': [],
                  'commands': {
                      'from_commands': [],
                      'user_commands': []
                    }
                  }
        for line in visited_children:
            if line[0]['type'] == "comment":
                content = line[0]['content']
                if content is not None and content != "":
                    result['comments'].append(content)
            if line[0]['type'] == "command":
                if line[0]['command_type'] == "from":
                    result['commands']['from_commands'].append(line[0]['content'])
                elif line[0]['command_type'] == "user":
                    result['commands']['user_commands'].append(line[0]['content'])
        return result

    # Functions for USER

    def visit_user_command(self, node, visited_children):
        _, _, user, _ = visited_children
        result = {'type': 'command',
                  'command_type': 'user',
                  'content': user[0]}
        return result

    def visit_user(self, node, visited_children):
        return "USER"

    def visit_user_name(self, node, visited_children):
        user, group = visited_children
        try:
            unix_group = group[0][1]
            return {'user': user, 'group': unix_group}
        except:
            return {'user': user, 'group': None}

    def visit_user_id(self, node, visited_children):
        user, group = visited_children
        try:
            unix_group = group[0][1]
            return {'user': user, 'group': unix_group}
        except:
            return {'user': user, 'group': None}

    def visit_unix_user(self, node, visited_children):
        return node.text

    def visit_unix_uid(self, node, visited_children):
        return node.text

    # END of functions for USER

    # Functions for FROM

    def visit_from_command(self, node, visited_children):
        _, _, platform, registry, image_name, tag_or_digest, local_name, _ = visited_children
        try:
            local_build_name = local_name[0]
        except:
            local_build_name = None
        try:
            registry_url = registry[0]
        except:
            registry_url = "Docker Hub"
        try:
            tag = tag_or_digest[0][0]
        except:
            tag = "latest"
        result = {"type": "command",
                  "command_type": "from",
                  "content":
                      {
                       "image": image_name.text,
                       "registry": registry_url,
                       "tag": tag,
                       "local_name": local_build_name,
                       },
                  "raw": node.text
                  }
        return result

    def visit_from(self, node, visited_children):
        return "FROM"

    def visit_platform(self, node, visited_children):
        _, platform, _ = visited_children
        return platform.text

    def visit_registry(self, node, visited_children):
        host, port, _ = visited_children
        try:
            port_number = port[0][1]
            registry_url = f"{host}:{port_number}"
        except:
            registry_url = host
        return registry_url

    def visit_host(self, node, visited_children):
        protocol, host = visited_children
        try:
            proto = protocol[0]
            return f"{proto}{host.text}"
        except:
            return host.text

    def visit_protocol(self, node, visited_children):
        return node.text

    def visit_port(self, node, visited_children):
        return node.text

    def visit_image_name(self, node, visited_children):
        return node

    def visit_image_tag(self, node, visited_children):
        _, tag = visited_children
        return tag.text

    def visit_digest(self, node, visited_children):
        _, algorithm, _, digest = visited_children
        return f"@{algorithm.text}:{digest.text}"

    def visit_local_name(self, node, visited_children):
        _, _, _, name = visited_children
        return name.text

    # END of Functions for FROM

    # Functions for COMMENT
    def visit_comment(self, node, visited_children):
        _, comment, _ = visited_children
        comment_sentence = ""
        for item in comment:
            comment_sentence += f"{item}"
        return {"type": "comment", "content": comment_sentence}

    def visit_sentence(self, node, visited_children):
        _, word, words = visited_children
        sentence = ""
        if word is not None:
            sentence += word.text
        if words[0][1] is not None:
            sentence += f" {words[0][1].text}"
        return sentence

    def visit_comment_start(self, node, visited_children):
        _, hashtag, _ = visited_children
        return hashtag.text

    # END of functions for COMMENT

    def visit_ws(self, node, visited_children):
        return node.text

    def generic_visit(self, node, visited_children):
        """ The generic visit method. """
        return visited_children or node


with open('Dockerfile') as f:
    data = f.read()
    #print(data)
    tree = grammar.parse(data)
    #print(tree)
    iv = IniVisitor()
    output = iv.visit(tree)
    print(json.dumps(output, indent=2))


