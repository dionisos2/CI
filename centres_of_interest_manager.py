"""
See CentresOfInterestManager class
"""

from xml.dom import minidom
from centre_of_interest import CentreOfInterest
from mylib.string_op import replace_special_char
import mylib.checking as checking
from mylib.Notifier import Notifier

class CentresOfInterestManager:
    """
    Class that permit to create/load lists of ci(center of interest),
    and to export them in different formats.
    """
    def __init__(self, list_of_ci=None, notifier=None):
        assert not(list_of_ci) or checking.is_all_instance(list_of_ci, CentreOfInterest)
        if notifier != None:
            assert isinstance(notifier, Notifier)

        self.notifier = notifier
        if list_of_ci == None:
            self.list_of_ci = []
        else:
            self.list_of_ci = list_of_ci

    def notify(self, text):
        """ notify something happening to the user (use the Notifier object) """
        if self.notifier != None:
            self.notifier.notify(text)

    def __iter__(self):
        for centre_of_interest in self.list_of_ci:
            yield centre_of_interest

    def __len__(self):
        return len(self.list_of_ci)

    def get_list_of_ci(self):
        """ get the list of ci managed """
        return self.list_of_ci

    def append(self, centre_of_interest):
        """ add a new centre of interest to be managed """
        assert isinstance(centre_of_interest, CentreOfInterest)
        self.list_of_ci.append(centre_of_interest)

    def __str__(self):
        tmp = ""
        for centre_of_interest in self.list_of_ci:
            tmp += str(centre_of_interest)
        return tmp

    def find(self, ci_name):
        """ find a centre of interest by name """
        assert isinstance(ci_name, str)
        for centre_of_interest in self:
            if centre_of_interest.name == ci_name:
                return centre_of_interest
        return None

    def load_xml(self, xml_file):
        """ load all the centres of interest from a xml file """
        self.notify('load xml_file "' + xml_file + '"')
        self.list_of_ci = []
        doc = minidom.parse(xml_file)
        for ci_node in doc.documentElement.getElementsByTagName("CI"):
            name = self._get_element(ci_node, "name")
            url = self._get_element(ci_node, "url")
            date = self._get_element(ci_node, "date")
            centre_of_interest = CentreOfInterest(name, url, date)
            self.append(centre_of_interest)

        self._load_children(doc)

    def _load_children(self, doc):
        """ Make the link between the centres of interest and their children """
        for ci_node in doc.documentElement.getElementsByTagName("CI"):
            ci_name = ci_node.getElementsByTagName("name")[0].firstChild.nodeValue
            centre_of_interest = self.find(ci_name)
            children_node = ci_node.getElementsByTagName("children")[0]
            for child in children_node.getElementsByTagName("child"):
                if child.firstChild == None:
                    raise ValueError("void child balise in '" + ci_name + "'")
                else:
                    child_name = child.firstChild.nodeValue
                child_ci = self.find(child_name)
                if child_ci != None:
                    centre_of_interest.add_child(child_ci)
                else:
                    raise ValueError("try to add the child : '" + child_name +
                                     "' to '" + ci_name + "' but the child was not found")

    @classmethod
    def _get_element(cls, ci_node, element):
        """ Get the element 'element', of the centre of interest node 'ci_node' """
        node = ci_node.getElementsByTagName(element)[0]

        if node.firstChild == None:
            return None
        else:
            return node.firstChild.nodeValue

    def sorted_by_name(self, translate=None):
        """
        Return the list of CI sorted by name.

        :param translate: a function used to translate the CI name,
        translate(ci_name)=ci_name_translated

        :type translate: function
        """
        if translate != None:
            return sorted(self.list_of_ci, key=lambda ci: translate(ci.get_name()))
        else:
            return sorted(self.list_of_ci, key=lambda ci: ci.get_name())

    def sorted_by_date(self, translate=None):
        """
        Return the list of CI sorted by date.

        :param translate: a function used to translate the CI name,
        translate(ci_name)=ci_name_translated

        :type translate: function
        """

        if translate == None:
            translate = lambda x: x

        def get_date_name(centre_of_interest):
            """ return a couple (ci_date, ci_name), to sort the list """
            if centre_of_interest.get_date() != None:
                return (centre_of_interest.get_date(), translate(centre_of_interest.get_name()))
            else:
                return ("", translate(centre_of_interest.get_name()))

        return sorted(self.list_of_ci, key=get_date_name)

    def to_html_list(self, order="by_name", translate=None):
        """
        Export the sorted list of CI to html.

        :param order: choose "by_name" to sort by name and "by_date" to sort by date
        :param translate: a function used to translate the CI name,
        translate(ci_name)=ci_name_translated
        :type order: str
        :type translate: function
        :return: return a string corresponding of the html page
        """

        if translate == None:
            translate = lambda x: x

        string = "<html>\n"
        string += "  <head>\n"
        string += '    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />'
        string += "  </head>\n"
        string += "  <body>\n"
        string += "    <ul>\n"

        if order == "by_name":
            sorted_list_of_ci = self.sorted_by_name(translate)
        elif order == "by_date":
            sorted_list_of_ci = self.sorted_by_date(translate)
        else:
            raise ValueError("order should be 'by_name', or 'by_date'. '"+order+"' given.")

        if (order == "by_date")and(len(sorted_list_of_ci) > 0):
            date = sorted_list_of_ci[0].get_date()
            if date != None:
                str_date = date
            else:
                str_date = "unknown"
            string += '      <h2>'+str_date+'</h2>'

        for centre_of_interest in sorted_list_of_ci:
            if (order == "by_date")and(centre_of_interest.get_date() != date):
                date = centre_of_interest.get_date()
                if date != None:
                    str_date = date
                else:
                    str_date = "unknown"

                string += '      <h2>'+str_date+'</h2>'

            string += '      <li><a href="' + centre_of_interest.get_url() + '">' + \
                      translate(centre_of_interest.get_name()) + '</a></li>\n'

        string += "    </ul>\n"
        string += "  </body>\n"
        string += "</html>\n"

        return string

    def to_graphviz(self, translate=None):
        """
        Export the sorted list of CI to a graphviz dot format.

        :param translate: a function used to translate the CI name,
        translate(ci_name)=ci_name_translated
        :type translate: function
        :return: return a string corresponding of the dot file
        """
        if translate == None:
            translate = lambda x: x

        string = "digraph CI {\n"
        string += '    node [fontcolor=blue, fontsize=8];\n'
        for centre_of_interest in self:
            string += '    "' + translate(centre_of_interest.get_name()) +\
                      '"[URL="'+centre_of_interest.url+ '"];\n'
            for child in centre_of_interest.get_children():
                string += '    "' + translate(centre_of_interest.get_name()) +\
                          '"->"' + translate(child.get_name()) + '";\n'
        string += "}"

        return replace_special_char(string)
