#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <libxml/parser.h>
#include <libxml/tree.h>
#include <libxml/xmlwriter.h>


int main(int argc, const char* argv[])
{
  const char * fileName = 0;
  for (int i = 1; i < argc; ++ i)
  {
    if ((strcmp(argv[i], "-x") == 0) && (i + 1 < argc)) 
    {
      fileName = argv[i + 1];
    }
  }

  const char *input_names[4];
  input_names[0] = "F";
  input_names[1] = "E";
  input_names[2] = "L";
  input_names[3] = "I";
  double input_values[4] = {0.0, 0.0, 0.0, 0.0};

  int compute_gradient = 0;

  xmlDoc *doc = xmlReadFile(fileName, NULL, 0);
  xmlNode *root_element = xmlDocGetRootElement(doc);
  xmlNode *cur = root_element->children;
  while (cur != NULL) {
    if ((!xmlStrcmp(cur->name, (const xmlChar *)"inputs")))
    {
      for (int i = 0; i < 4; ++ i)
      {
        xmlChar * attr = xmlGetProp(cur, (const xmlChar *)input_names[i]);
        input_values[i] = atof((const char *)attr);
//         printf("%s=%e\n", input_names[i], input_values[i]);
      }
    }
    if ((!xmlStrcmp(cur->name, (const xmlChar *)"computation")))
    {
      xmlNode *computation = cur->children;
      while (computation != NULL) {
        if ((!xmlStrcmp(computation->name, (const xmlChar *)"derivate"))) {
          xmlChar * activate = xmlGetProp(computation, (const xmlChar *)"activate");
          compute_gradient = !strcmp(activate, "on");
        }
        computation = computation->next;
      }
    }
    cur = cur->next;
  }
  xmlFreeDoc(doc);
  xmlCleanupParser();

  double F = input_values[0];
  double E = input_values[1];
  double L = input_values[2];
  double I = input_values[3];
  double deviation = F * L * L * L / (3.0 * E * I);
//   printf("deviation=%e\n", deviation);

  xmlTextWriterPtr writer = xmlNewTextWriterFilename("_beam_outputs_.xml", 0);
  xmlTextWriterStartDocument(writer, NULL, "UTF-8", NULL);
  xmlTextWriterStartElement(writer, "beam");
    xmlTextWriterStartElement(writer, "description");
      xmlTextWriterWriteAttribute(writer, "name", "beam");
      xmlTextWriterWriteAttribute(writer, "title", "UseCase beam with XML input file");
      xmlTextWriterWriteAttribute(writer, "version", "1.0");
      xmlTextWriterWriteAttribute(writer, "date", "2014-04-07");
      xmlTextWriterStartElement(writer, "tool");
        xmlTextWriterWriteAttribute(writer, "name", "beam exe");
        xmlTextWriterWriteAttribute(writer, "version", "1.0");
      xmlTextWriterEndElement(writer);
    xmlTextWriterEndElement(writer);
    xmlTextWriterStartElement(writer, "inputs");
    for (int i = 0; i < 4; ++ i)
    {
      char value_str[256];
      memset(value_str, 0, 256*sizeof(char));
      sprintf(value_str, "%e", input_values[i]);
      xmlTextWriterWriteAttribute(writer, input_names[i], value_str);
    }
    xmlTextWriterEndElement(writer); // inputs
    xmlTextWriterStartElement(writer, "computation");
      xmlTextWriterStartElement(writer, "derivate");
        xmlTextWriterWriteAttribute(writer, "activate", compute_gradient ? "on" : "off");
      xmlTextWriterEndElement(writer); // derivate
      xmlTextWriterStartElement(writer, "hessian");
        xmlTextWriterWriteAttribute(writer, "activate", "off");
      xmlTextWriterEndElement(writer); // hessian
    xmlTextWriterEndElement(writer); // computation
    
    xmlTextWriterStartElement(writer, "outputs");
      char value_str[256];
      memset(value_str, 0, 256*sizeof(char));
      sprintf(value_str, "%e", deviation);
      xmlTextWriterWriteAttribute(writer, "deviation", value_str);
    xmlTextWriterEndElement(writer); // outputs

    if (compute_gradient)
    {
      xmlTextWriterStartElement(writer, "derivates");
      for (int i = 0; i < 4; ++ i)
      {
        char value_str[256];
        memset(value_str, 0, 256*sizeof(char));
        sprintf(value_str, "%e", input_values[i]);
        char name_str[256];
        memset(name_str, 0, 256*sizeof(char));
        sprintf(name_str, "partial%s", input_names[i]);
        xmlTextWriterWriteAttribute(writer, name_str, "-1.0");
      }
      xmlTextWriterEndElement(writer); // derivates
    }

    xmlTextWriterStartElement(writer, "hessian");
    xmlTextWriterEndElement(writer); // hessian
 
  xmlTextWriterEndElement(writer);
  xmlTextWriterEndDocument(writer);
  xmlFreeTextWriter(writer);
  return 0;
}

