import scrapy

class OneSpider(scrapy.Spider):
    name = "one"
    allowed_domains = ["attack.mitre.org"]
    start_urls = ["https://attack.mitre.org/tactics/ics/"]

    def parse(self, response):
        rows = response.xpath('//table[@class="table table-bordered table-alternate mt-2"]/tbody/tr')
        for row in rows:
            id = row.xpath('./td[1]/a/text()').get()
            name = row.xpath('./td[2]/a/text()').get()
            description = row.xpath('./td[3]/text()').get()
            url = response.urljoin(row.xpath('./td[1]/a/@href').get())

            item = {
                'id': id,
                'name': name,
                'description': description.strip() if description else '',
                'url': url
            }

            # Schedule a request to the tactic detail page, passing the item via meta
            request = scrapy.Request(url=url, callback=self.parse_tactic_details)
            request.meta['item'] = item
            yield request

    def parse_tactic_details(self, response):
        item = response.meta['item']

        techniques = []
        rows = response.xpath('//table[@class="table-techniques"]/tbody/tr')
        for row in rows:
            technique_id = row.xpath('./td[1]//a/text()').get()
            technique_name = row.xpath('./td[2]//a/text()').get()
            technique_description = row.xpath('./td[3]/text()').get()
            technique_url = response.urljoin(row.xpath('./td[1]//a/@href').get())

            technique = {
                'technique_id': technique_id.strip() if technique_id else '',
                'technique_name': technique_name.strip() if technique_name else '',
                'technique_description': technique_description.strip() if technique_description else '',
                'technique_url': technique_url
            }

            techniques.append(technique)

            # Schedule a request to the technique detail page, passing the technique via meta
            request = scrapy.Request(url=technique_url, callback=self.parse_technique_details)
            request.meta['technique'] = technique
            yield request

        item['techniques'] = techniques
        yield item

    def parse_technique_details(self, response):
        technique = response.meta['technique']

        procedure_examples = []
        rows = response.xpath('//div[@class="tables-mobile"]//table[contains(@class, "table")]/tbody/tr')
        for row in rows:
            procedure_id = row.xpath('./td[1]/a/text()').get()
            procedure_name = row.xpath('./td[2]/a/text()').get()
            procedure_description = row.xpath('./td[3]/p/text()').get()

            procedure_examples.append({
                'procedure_id': procedure_id.strip() if procedure_id else '',
                'procedure_name': procedure_name.strip() if procedure_name else '',
                'procedure_description': procedure_description.strip() if procedure_description else ''
            })

        technique['procedure_examples'] = procedure_examples

        self.log(f"Scraped Procedure Examples: {procedure_examples}")

        yield technique
