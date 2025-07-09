import { Injectable } from "@nestjs/common";

@Injectable()
export class livecheckService{

    livecheckStatus():string{
        return "up and working"
    }

}