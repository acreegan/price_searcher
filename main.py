import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from bs4 import BeautifulSoup
from urllib.request import urlopen
import math

url = "https://www.wakefieldmetals.co.nz/cuts/"

BrassDensity = 0.00000873 # kg / mm^3
WakefieldPrice =  19.4435 # $/kg excl GST
GST = .15 # GST %

def main(data, context):
    try:
        html = urlopen(url).read().decode('utf-8')
        soup = BeautifulSoup(html,'html.parser')

        # Table of brass offcuts should be the 4th table on the page
        rows = soup.findAll("table")[3].find_all("tr")

    except Exception as e:
        print("Error geting data from wakefield metals website:", e)

    else:
        for row in rows:
            try:
                form = row.findAll("td")[1].string
                dimensions = row.findAll("td")[3].string.split(" x ")
            except Exception as e:
                print("Brass table not in expected shape")
            else:
                if form == "Flat Bar":
                    try:
                        x = float(dimensions[0])
                        y = float(dimensions[1])
                        z = float(dimensions[2])

                        volume = x*y*z
                        mass = volume * BrassDensity
                        priceEXGST = mass * WakefieldPrice
                        price = priceEXGST * (1+GST)

                        cell = soup.new_tag("td")
                        cell.string = "$%.2f" % price
                        row.append(cell)

                    except Exception as e:
                        print("Error calculating price: ", e)

                elif form == "Hexagonal Bar":
                    try:
                        d = float(dimensions[0])
                        length = float(dimensions[1])

                        apothem = d/2
                        x = apothem/math.sqrt(3)
                        side = 2*x
                        perimeter = 6*side
                        area = (perimeter*apothem)/2

                        volume = length*area
                        mass = volume * BrassDensity
                        priceEXGST = mass * WakefieldPrice
                        price = priceEXGST * (1+GST)

                        cell = soup.new_tag("td")
                        cell.string = "$%.2f" % price
                        row.append(cell)
                    except Exception as e:
                        print("Error calculating price: " + e)

                elif form == "Round Bar":
                    try:
                        d = float(dimensions[0])
                        length = float(dimensions[1])

                        volume = length*((math.pi * d**2)/4)
                        mass = volume * BrassDensity
                        priceEXGST = mass * WakefieldPrice
                        price = priceEXGST * (1+GST)

                        cell = soup.new_tag("td")
                        cell.string = "$%.2f" % price
                        row.append(cell)
                    except Exception as e:
                        print("Error calculating price: " + e)
                elif form == "Square Bar":
                    try:
                        x = float(dimensions[0])
                        length = float(dimensions[1])

                        volume = length * x**2
                        mass = volume * BrassDensity
                        priceEXGST = mass * WakefieldPrice
                        price = priceEXGST * (1 + GST)

                        cell = soup.new_tag("td")
                        cell.string = "$%.2f" % price
                        row.append(cell)
                    except Exception as e:
                        print("Error calculating price: " + e)
                else:
                    print("Unrecognized Form")

                rows.sort(key=myFunc)
                table = soup.new_tag("table",style="text-align:left")
                header = soup.new_tag("tr")
                itemNo = soup.new_tag("th")
                itemNo.string="Item No"
                form = soup.new_tag("th")
                form.string="Form"
                description = soup.new_tag("th")
                description.string="Item Description"
                dimensions = soup.new_tag("th")
                dimensions.string="Dimensions"
                Alloy = soup.new_tag("th")
                Alloy.string="Alloy"
                tag = soup.new_tag("th")
                tag.string="Stock Tag"
                priceHeader = soup.new_tag("th")
                priceHeader.string="Calculated Price"
                header.extend([itemNo,form,description,dimensions,Alloy,tag,priceHeader])

                table.append(header)
                table.extend(rows)


    message = Mail(
        from_email='andrew@covid19-cases.nz',
        to_emails='andrew.s.creegan@gmail.com',
        subject='Wakefield Metals Brass Offcut Prices',
        html_content=str(table))
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)



def myFunc(e):
    try:
        return float(e.findAll("td")[6].string.strip("$"))
        # return float(e.findAll("td")[0].string)
    except Exception:
        return float("inf")

if __name__ == "__main__":
    main(0,0)