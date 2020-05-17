import requests
import re
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt


class COVID19:
    '''
        this class crawls all covid 19 new cases and death cases of all countries in a time-series from
        the official world health organization website: https://www.worldometers.info/coronavirus/
    '''
    def __init__(self):
        self.main_page_url = 'https://www.worldometers.info/coronavirus/'
        self._country_data = None
        self._country_zero_pad_cases = None
        self._country_cases = None

    @property
    def country_cases(self):
        if self._country_cases is not None:
            return self._country_cases

        country_cases = {}
        for country in self.country_data:
            for data in self.country_data[country]:
                if data['name'] == 'Cases':
                    country_cases[country] = data['data']

        self._country_cases = country_cases

        return self._country_cases

    @property
    def country_data(self):
        return self._country_data

    @property
    def country_zero_pad_cases(self):
        return self._country_zero_pad_cases

    def crawl(self, *, top_n_countries=10):
        '''
        main crawler function
        :param top_n_countries: the number of countries you wish to crawl
        :return: dictionary of country data
        '''
        if self.country_data is not None:
            return self.country_data

        main_page = requests.get(self.main_page_url)

        soup = BeautifulSoup(main_page.text, 'html.parser')

        anchor_tags = soup.select('#main_table_countries_today a.mt_a')

        counter = 0
        country_data = {}
        for tag in anchor_tags:
            counter += 1
            if counter > top_n_countries:
                break
            country = tag.text

            href = tag.get('href')

            country_url = self.main_page_url + href

            response = requests.get(country_url)

            text = response.text

            text = ''.join(''.join(text.split('\n')).split(' '))

            regex = re.compile(r'series:\[\{.*?\}\]', re.MULTILINE | re.IGNORECASE)

            results = regex.findall(text)

            output = []
            for result in results:
                try:
                    clean = result[8:-1]
                    clean = clean.replace('name:', '"name":')
                    clean = clean.replace('color:', '"color":')
                    clean = clean.replace('lineWidth:', '"lineWidth":')
                    clean = clean.replace('data:', '"data":')
                    clean = 'None'.join(clean.split('null'))
                    clean = 'None'.join(clean.split('"nan"'))

                    run_code = eval(clean)
                    if isinstance(run_code, tuple):
                        run_code = run_code[0]
                    output.append(run_code)
                except:
                    pass

            unique_results = []
            already_seen = set()
            for res in output:
                if res['name'] in already_seen:
                    continue

                unique_results.append({
                    'name': res['name'],
                    'data': res['data']
                })

                already_seen.add(res['name'])

            country_data[country] = unique_results
            print(f'country {country} has been crawled successfully!')

        self._country_data = country_data
        return self.country_data

    def zero_pad_new_cases(self):
        if self._country_zero_pad_cases is not None:
            return self._country_zero_pad_cases

        zero_pad_cases = {}
        max_length_data = 0
        for country in self.country_cases:
            data_length = len(self.country_cases[country])
            if max_length_data < data_length:
                max_length_data = data_length

        for country in self.country_cases:
            data_length = len(self.country_cases[country])
            difference = max_length_data - data_length
            zero_pad_cases[country] = [0 for x in range(difference)] + self.country_cases[country]

        self._country_zero_pad_cases = zero_pad_cases
        return self.country_zero_pad_cases

    def plot_cases(self):
        self.zero_pad_new_cases()

        legends = []
        plt.figure(figsize=(20, 10))
        for country in self.country_zero_pad_cases:
            plt.plot(self.country_zero_pad_cases[country])
            legends.append(country)
        plt.legend(legends)
        plt.grid()
        plt.show()


if __name__ == '__main__':
    covid = COVID19()
    country_data = covid.crawl()
    covid.plot_cases()

    print('\nAll Countries Data:\n\n')
    print(country_data)
