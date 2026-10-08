import re

with open('frontend/app/register/page.tsx', 'r') as f:
    content = f.read()

new_catch = """    } catch(err: any) {
      let errMsg = "Registration failed";
      if (err.response && err.response.data) {
        if (typeof err.response.data.error === 'string') {
          errMsg = err.response.data.error;
        } else if (typeof err.response.data === 'string') {
          errMsg = err.response.data;
        } else {
          errMsg = JSON.stringify(err.response.data);
        }
      } else if (err.message) {
        errMsg = err.message;
      }
      alert(errMsg);
    }"""

content = re.sub(r'\} catch\(err: any\) \{[^}]*\}', new_catch, content, flags=re.MULTILINE)

with open('frontend/app/register/page.tsx', 'w') as f:
    f.write(content)
